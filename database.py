import sqlite3
from pathlib import Path


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():
    """
    Return a SQLite connection with rows accessible
    using column names.
    """

    conn = sqlite3.connect(DATABASE)

    # Allows:
    # row["username"]
    # row["fullname"]
    # row["id"]

    conn.row_factory = sqlite3.Row

    # Enable foreign-key support
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# ============================================================
# CREATE USER PROGRESS + CERTIFICATE TABLES
# ============================================================

def create_user_progress_tables(conn):
    """
    Create tables required for:
        1. User-wise solved problems
        2. Certificate generation

    IMPORTANT:
    These tables are NOT deleted when problems are reseeded.
    Therefore user progress remains permanent.
    """

    # ========================================================
    # USER PROBLEM PROGRESS
    # ========================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_problem_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            problem_id INTEGER NOT NULL,

            language TEXT NOT NULL,

            solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(user_id, problem_id, language),

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)


    # ========================================================
    # CERTIFICATES
    # ========================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL UNIQUE,

            certificate_id TEXT NOT NULL UNIQUE,

            issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)


    # ========================================================
    # INDEXES
    # ========================================================

    # Faster progress lookup
    conn.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_progress_user
        ON user_problem_progress(user_id)
    """)


    # Faster language-wise lookup
    conn.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_progress_user_language
        ON user_problem_progress(user_id, language)
    """)


    # Faster problem lookup
    conn.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_progress_problem
        ON user_problem_progress(problem_id)
    """)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():
    """
    Create/reset the problems table and insert all 135 problems.

    IMPORTANT:
    Only the problems table is rebuilt.

    User progress and certificates are NEVER deleted.
    """

    conn = get_db()

    try:

        # ====================================================
        # PROBLEMS TABLE
        # ====================================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                example_input TEXT,
                example_output TEXT
            )
        """)
        # ============================================================
# LANGUAGE CERTIFICATES TABLE
# ============================================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS language_certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                language TEXT NOT NULL,
                certificate_id TEXT NOT NULL UNIQUE,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, language)
            )
        """)

        # ====================================================
        # USER PROGRESS + CERTIFICATE TABLES
        # ====================================================

        create_user_progress_tables(conn)


        # ====================================================
        # REBUILD PROBLEM BANK
        # ====================================================

        conn.execute("DELETE FROM problems")


        conn.executemany("""
            INSERT INTO problems
            (
                id,
                title,
                difficulty,
                category,
                description,
                example_input,
                example_output
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, PROBLEMS)


        conn.commit()


        # ====================================================
        # PRINT DATABASE INFORMATION
        # ====================================================

        print("========================================")
        print("Database created successfully.")
        print(f"Database: {DATABASE}")
        print(f"Problems inserted: {len(PROBLEMS)}")
        print("Easy: 45 | Medium: 45 | Hard: 45")
        print("User progress table: READY")
        print("Certificates table: READY")
        print("========================================")


    except Exception as e:

        conn.rollback()

        print("DATABASE INITIALIZATION ERROR:")
        print(e)

        raise

    finally:

        conn.close()


# ============================================================
# SEED PROBLEMS
# ============================================================

def seed_problems():
    """
    Rebuild the problem bank.

    User progress and certificate information
    will NOT be deleted.
    """

    conn = get_db()

    try:

        # ====================================================
        # PROBLEMS TABLE
        # ====================================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                example_input TEXT,
                example_output TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_problem_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                problem_id INTEGER NOT NULL,
                language TEXT NOT NULL,
                solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, problem_id, language)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                certificate_id TEXT NOT NULL UNIQUE,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()   

        # ====================================================
        # USER PROGRESS + CERTIFICATES
        # ====================================================

        create_user_progress_tables(conn)


        # ====================================================
        # DELETE ONLY PROBLEMS
        # ====================================================

        conn.execute("DELETE FROM problems")


        # ====================================================
        # INSERT ALL PROBLEMS
        # ====================================================

        conn.executemany("""
            INSERT INTO problems
            (
                id,
                title,
                difficulty,
                category,
                description,
                example_input,
                example_output
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, PROBLEMS)


        conn.commit()


        print("========================================")
        print("135 problems inserted successfully!")
        print("User progress preserved.")
        print("Certificates preserved.")
        print("========================================")


    except Exception as e:

        conn.rollback()

        print("SEED ERROR:")
        print(e)

        raise

    finally:

        conn.close()


# ============================================================
# SEED ONLY IF EMPTY
# ============================================================

def seed_if_empty():
    """
    Seed the database only if the problems table is empty.
    """

    conn = get_db()

    try:

        # Check whether problems table exists
        table = conn.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'problems'
        """).fetchone()


        # If problems table doesn't exist,
        # initialize everything.
        if not table:

            conn.close()

            init_db()

            return


        # ====================================================
        # CHECK PROBLEM COUNT
        # ====================================================

        row = conn.execute("""
            SELECT COUNT(*) AS count
            FROM problems
        """).fetchone()

        count = row["count"]


        # ====================================================
        # ALWAYS MAKE SURE PROGRESS TABLES EXIST
        # ====================================================

        create_user_progress_tables(conn)

        conn.commit()


    finally:

        conn.close()


    # ========================================================
    # SEED ONLY IF NO PROBLEMS
    # ========================================================

    if count == 0:

        init_db()


PROBLEMS = [
    (1, 'Two Sum', 'Easy', 'Arrays', 'Given an array of integers and a target, return the indices of two numbers that add up to the target.', '[2, 7, 11, 15], target = 9', '[0, 1]'),
    (2, 'Best Time to Buy and Sell Stock', 'Easy', 'Arrays', 'Given daily stock prices, find the maximum profit from one buy followed by one sell.', '[7, 1, 5, 3, 6, 4]', '5'),
    (3, 'Contains Duplicate', 'Easy', 'Arrays', 'Return true if any value appears at least twice in the array; otherwise return false.', '[1, 2, 3, 1]', 'true'),
    (4, 'Maximum Subarray', 'Easy', 'Arrays', 'Find the contiguous subarray with the largest sum and return its sum.', '[-2,1,-3,4,-1,2,1,-5,4]', '6'),
    (5, 'Move Zeroes', 'Easy', 'Arrays', 'Move all zeroes to the end of the array while keeping the relative order of non-zero elements.', '[0,1,0,3,12]', '[1,3,12,0,0]'),
    (6, 'Product of Array Except Self', 'Medium', 'Arrays', 'Return an array where each position contains the product of all other elements without using division.', '[1,2,3,4]', '[24,12,8,6]'),
    (7, '3Sum', 'Medium', 'Arrays', 'Find all unique triplets whose values add up to zero.', '[-1,0,1,2,-1,-4]', '[[-1,-1,2],[-1,0,1]]'),
    (8, 'Container With Most Water', 'Medium', 'Arrays', 'Choose two lines that form a container holding the maximum amount of water.', '[1,8,6,2,5,4,8,3,7]', '49'),
    (9, 'Subarray Sum Equals K', 'Medium', 'Arrays', 'Count the number of continuous subarrays whose sum equals k.', '[1,1,1], k = 2', '2'),
    (10, 'Rotate Array', 'Medium', 'Arrays', 'Rotate the array to the right by k positions.', '[1,2,3,4,5,6,7], k = 3', '[5,6,7,1,2,3,4]'),
    (11, 'Trapping Rain Water', 'Hard', 'Arrays', 'Given bar heights, compute how much rain water can be trapped.', '[0,1,0,2,1,0,1,3,2,1,2,1]', '6'),
    (12, 'First Missing Positive', 'Hard', 'Arrays', 'Find the smallest missing positive integer in an unsorted array.', '[3,4,-1,1]', '2'),
    (13, 'Maximum Product Subarray', 'Hard', 'Arrays', 'Find the contiguous subarray with the largest product.', '[2,3,-2,4]', '6'),
    (14, 'Sliding Window Maximum', 'Hard', 'Arrays', 'Return the maximum value in every sliding window of size k.', '[1,3,-1,-3,5,3,6,7], k = 3', '[3,3,5,5,6,7]'),
    (15, 'Median of Two Sorted Arrays', 'Hard', 'Arrays', 'Find the median of two sorted arrays in logarithmic time.', '[1,3], [2]', '2.0'),
    (16, 'Valid Anagram', 'Easy', 'Strings', 'Determine whether two strings contain the same characters with the same frequencies.', 's = "anagram", t = "nagaram"', 'true'),
    (17, 'Valid Palindrome', 'Easy', 'Strings', 'Return true if a string is a palindrome after ignoring non-alphanumeric characters and case.', '"A man, a plan, a canal: Panama"', 'true'),
    (18, 'Longest Common Prefix', 'Easy', 'Strings', 'Find the longest common prefix shared by all strings in an array.', '["flower","flow","flight"]', '"fl"'),
    (19, 'Reverse String', 'Easy', 'Strings', 'Reverse a character array in place.', '["h","e","l","l","o"]', '["o","l","l","e","h"]'),
    (20, 'First Unique Character', 'Easy', 'Strings', 'Return the index of the first character that occurs only once.', '"leetcode"', '0'),
    (21, 'Longest Substring Without Repeating Characters', 'Medium', 'Strings', 'Find the length of the longest substring containing no repeated characters.', '"abcabcbb"', '3'),
    (22, 'Group Anagrams', 'Medium', 'Strings', 'Group strings that are anagrams of each other.', '["eat","tea","tan","ate","nat","bat"]', '[["eat","tea","ate"],["tan","nat"],["bat"]]'),
    (23, 'Longest Palindromic Substring', 'Medium', 'Strings', 'Find the longest palindromic substring in a given string.', '"babad"', '"bab"'),
    (24, 'String to Integer (atoi)', 'Medium', 'Strings', 'Convert a string to a 32-bit signed integer following standard atoi rules.', '"   -42"', '-42'),
    (25, 'Permutation in String', 'Medium', 'Strings', 'Determine whether one string contains a permutation of another string.', 's1 = "ab", s2 = "eidbaooo"', 'true'),
    (26, 'Minimum Window Substring', 'Hard', 'Strings', 'Find the smallest substring of s that contains every character of t with required frequencies.', 's = "ADOBECODEBANC", t = "ABC"', '"BANC"'),
    (27, 'Regular Expression Matching', 'Hard', 'Strings', 'Implement matching of a string against a pattern containing . and *.', 's = "aab", p = "c*a*b"', 'true'),
    (28, 'Word Break II', 'Hard', 'Strings', 'Return all possible sentences formed by splitting a string into dictionary words.', 's = "catsanddog", words = ["cat","cats","and","sand","dog"]', '["cats and dog","cat sand dog"]'),
    (29, 'Edit Distance', 'Hard', 'Strings', 'Find the minimum number of insertions, deletions, and replacements needed to transform one word into another.', 'word1 = "horse", word2 = "ros"', '3'),
    (30, 'Distinct Subsequences', 'Hard', 'Strings', 'Count how many distinct subsequences of s equal t.', 's = "rabbbit", t = "rabbit"', '3'),
    (31, 'Palindrome Number', 'Easy', 'Math', 'Determine whether an integer reads the same forward and backward.', '121', 'true'),
    (32, 'Reverse Integer', 'Easy', 'Math', 'Reverse the digits of a signed 32-bit integer and return 0 on overflow.', '123', '321'),
    (33, 'Fizz Buzz', 'Easy', 'Math', 'Return Fizz for multiples of 3, Buzz for multiples of 5, and FizzBuzz for both.', 'n = 5', '["1","2","Fizz","4","Buzz"]'),
    (34, 'Count Primes', 'Easy', 'Math', 'Count the number of prime numbers strictly less than n.', 'n = 10', '4'),
    (35, 'Power of Two', 'Easy', 'Math', 'Determine whether an integer is a power of two.', '16', 'true'),
    (36, 'Pow(x, n)', 'Medium', 'Math', 'Compute x raised to the integer power n efficiently.', 'x = 2.0, n = 10', '1024.0'),
    (37, 'Happy Number', 'Medium', 'Math', 'Determine whether repeatedly replacing a number by the sum of squared digits eventually reaches 1.', '19', 'true'),
    (38, 'Integer Break', 'Medium', 'Math', 'Split n into at least two positive integers to maximize their product.', 'n = 10', '36'),
    (39, 'Factorial Trailing Zeroes', 'Medium', 'Math', 'Count the number of trailing zeroes in n factorial.', 'n = 25', '6'),
    (40, 'Divide Two Integers', 'Medium', 'Math', 'Divide two integers without using multiplication, division, or modulo operators.', '10, 3', '3'),
    (41, 'Max Points on a Line', 'Hard', 'Math', 'Find the maximum number of points that lie on the same straight line.', '[[1,1],[2,2],[3,3]]', '3'),
    (42, 'Basic Calculator', 'Hard', 'Math', 'Evaluate a string expression containing non-negative integers, plus, minus, and parentheses.', '"1 + (2 - 3) + 4"', '4'),
    (43, 'Basic Calculator II', 'Hard', 'Math', 'Evaluate an expression containing integers and +, -, *, / with standard precedence.', '"3+2*2"', '7'),
    (44, 'Integer to Roman Advanced', 'Hard', 'Math', 'Convert an integer to its Roman numeral representation.', '1994', '"MCMXCIV"'),
    (45, 'Number of Digit One', 'Hard', 'Math', 'Count how many times digit 1 appears in all integers from 1 through n.', 'n = 13', '6'),
    (46, 'Reverse Linked List', 'Easy', 'Linked List', 'Reverse a singly linked list.', '[1,2,3,4,5]', '[5,4,3,2,1]'),
    (47, 'Merge Two Sorted Lists', 'Easy', 'Linked List', 'Merge two sorted linked lists into one sorted linked list.', '[1,2,4], [1,3,4]', '[1,1,2,3,4,4]'),
    (48, 'Linked List Cycle', 'Easy', 'Linked List', 'Determine whether a linked list contains a cycle.', '3 -> 2 -> 0 -> -4, tail connects to node 2', 'true'),
    (49, 'Remove Duplicates from Sorted List', 'Easy', 'Linked List', 'Remove duplicate values from a sorted linked list.', '[1,1,2,3,3]', '[1,2,3]'),
    (50, 'Middle of the Linked List', 'Easy', 'Linked List', 'Return the middle node of a singly linked list.', '[1,2,3,4,5]', '[3,4,5]'),
    (51, 'Add Two Numbers', 'Medium', 'Linked List', 'Add two non-negative integers represented by reversed linked lists.', '[2,4,3], [5,6,4]', '[7,0,8]'),
    (52, 'Remove Nth Node From End', 'Medium', 'Linked List', 'Remove the nth node from the end of a linked list.', '[1,2,3,4,5], n = 2', '[1,2,3,5]'),
    (53, 'Reorder List', 'Medium', 'Linked List', 'Reorder a list as first, last, second, second-last, and so on.', '[1,2,3,4]', '[1,4,2,3]'),
    (54, 'Copy List With Random Pointer', 'Medium', 'Linked List', 'Deep-copy a linked list whose nodes contain next and random pointers.', 'nodes = [[7,null],[13,0],[11,4],[10,2],[1,0]]', 'deep copy of the same structure'),
    (55, 'Sort List', 'Medium', 'Linked List', 'Sort a linked list in ascending order.', '[4,2,1,3]', '[1,2,3,4]'),
    (56, 'Merge K Sorted Lists', 'Hard', 'Linked List', 'Merge k sorted linked lists into one sorted linked list.', '[[1,4,5],[1,3,4],[2,6]]', '[1,1,2,3,4,4,5,6]'),
    (57, 'Reverse Nodes in K Group', 'Hard', 'Linked List', 'Reverse linked-list nodes in groups of k while leaving incomplete groups unchanged.', '[1,2,3,4,5], k = 2', '[2,1,4,3,5]'),
    (58, 'LRU Cache', 'Hard', 'Linked List', 'Design a least-recently-used cache with O(1) get and put operations.', 'capacity = 2; put(1,1); put(2,2); get(1); put(3,3)', 'get(2) returns -1'),
    (59, 'Palindrome Linked List', 'Hard', 'Linked List', 'Determine whether the values in a linked list form a palindrome.', '[1,2,2,1]', 'true'),
    (60, 'Intersection of Two Linked Lists', 'Hard', 'Linked List', 'Find the node where two singly linked lists intersect.', 'A = [4,1,8,4,5], B = [5,6,1,8,4,5]', 'node value 8'),
    (61, 'Valid Parentheses', 'Easy', 'Stack', 'Determine whether brackets in a string are correctly matched and nested.', '"()[]{}"', 'true'),
    (62, 'Min Stack', 'Easy', 'Stack', 'Design a stack supporting push, pop, top, and minimum retrieval in constant time.', 'push(-2), push(0), push(-3), getMin()', '-3'),
    (63, 'Implement Stack Using Queues', 'Easy', 'Stack', 'Implement stack operations using one or more queues.', 'push(1), push(2), top()', '2'),
    (64, 'Remove All Adjacent Duplicates', 'Easy', 'Stack', 'Repeatedly remove adjacent equal character pairs.', '"abbaca"', '"ca"'),
    (65, 'Backspace String Compare', 'Easy', 'Stack', 'Compare two strings after processing # as a backspace.', 's = "ab#c", t = "ad#c"', 'true'),
    (66, 'Daily Temperatures', 'Medium', 'Stack', 'For each day, find how many days must pass before a warmer temperature.', '[73,74,75,71,69,72,76,73]', '[1,1,4,2,1,1,0,0]'),
    (67, 'Evaluate Reverse Polish Notation', 'Medium', 'Stack', 'Evaluate an arithmetic expression written in reverse Polish notation.', '["2","1","+","3","*"]', '9'),
    (68, 'Decode String', 'Medium', 'Stack', 'Decode strings encoded using k[encoded_string] notation.', '"3[a2[c]]"', '"accaccacc"'),
    (69, 'Simplify Path', 'Medium', 'Stack', 'Simplify an absolute Unix-style file path.', '"/home//foo/../bar/"', '"/home/bar"'),
    (70, 'Next Greater Element', 'Medium', 'Stack', 'For each element, find the next greater element to its right.', '[2,1,2,4,3]', '[4,2,4,-1,-1]'),
    (71, 'Largest Rectangle in Histogram', 'Hard', 'Stack', 'Find the largest rectangle area that can be formed in a histogram.', '[2,1,5,6,2,3]', '10'),
    (72, 'Maximal Rectangle', 'Hard', 'Stack', 'Find the largest rectangle containing only 1s in a binary matrix.', '[["1","0","1","0","0"],["1","0","1","1","1"],["1","1","1","1","1"],["1","0","0","1","0"]]', '6'),
    (73, 'Basic Calculator', 'Hard', 'Stack', 'Evaluate an arithmetic expression with integers, plus, minus, and parentheses.', '"1-(2+3)"', '-4'),
    (74, 'Trapping Rain Water Using Stack', 'Hard', 'Stack', 'Compute trapped rain water using a monotonic stack approach.', '[4,2,0,3,2,5]', '9'),
    (75, 'Remove Duplicate Letters', 'Hard', 'Stack', 'Remove duplicate letters so every letter appears once and the result is lexicographically smallest.', '"cbacdcbc"', '"acdb"'),
    (76, 'Implement Queue Using Stacks', 'Easy', 'Queue', 'Implement FIFO queue operations using stacks.', 'push(1), push(2), peek()', '1'),
    (77, 'Number of Recent Calls', 'Easy', 'Queue', 'Count requests made within the last 3000 milliseconds.', 'ping(1), ping(100), ping(3001)', '[1,2,1]'),
    (78, 'Design Circular Queue', 'Easy', 'Queue', 'Design a fixed-size circular queue supporting enqueue and dequeue.', 'k=3; enQueue(1), enQueue(2), enQueue(3), enQueue(4)', 'false for enQueue(4)'),
    (79, 'Moving Average from Data Stream', 'Easy', 'Queue', 'Return the moving average of the last size values in a data stream.', 'size=3; next(1), next(10), next(3)', '[1.0,5.5,4.6667]'),
    (80, 'Time Needed to Buy Tickets', 'Easy', 'Queue', 'Find how long it takes for a person at index k to finish buying tickets.', 'tickets=[2,3,2], k=2', '6'),
    (81, 'Rotting Oranges', 'Medium', 'Queue', 'Find the minutes needed for all reachable fresh oranges to become rotten.', '[[2,1,1],[1,1,0],[0,1,1]]', '4'),
    (82, 'Open the Lock', 'Medium', 'Queue', 'Find the minimum turns needed to reach a target lock combination while avoiding deadends.', 'deadends=["0201","0101","0102","1212","2002"], target="0202"', '6'),
    (83, 'Perfect Squares', 'Medium', 'Queue', 'Return the least number of perfect square numbers that sum to n.', 'n=12', '3'),
    (84, 'Dota2 Senate', 'Medium', 'Queue', 'Simulate a queue-based senate voting process and determine the winning party.', '"RDD"', '"Dire"'),
    (85, 'Task Scheduler', 'Medium', 'Queue', 'Schedule tasks with a cooldown interval while minimizing total execution time.', 'tasks=["A","A","A","B","B","B"], n=2', '8'),
    (86, 'Sliding Window Maximum', 'Hard', 'Queue', 'Return the maximum value in each sliding window using a deque.', '[1,3,-1,-3,5,3,6,7], k=3', '[3,3,5,5,6,7]'),
    (87, 'Shortest Subarray With Sum at Least K', 'Hard', 'Queue', 'Find the shortest non-empty subarray whose sum is at least k.', '[2,-1,2], k=3', '3'),
    (88, 'Constrained Subsequence Sum', 'Hard', 'Queue', 'Find the maximum subsequence sum where chosen indices differ by at most k.', '[10,2,-10,5,20], k=2', '37'),
    (89, 'Jump Game VI', 'Hard', 'Queue', 'Find the maximum score when jumping forward at most k positions.', '[1,-1,-2,4,-7,3], k=2', '7'),
    (90, 'Design Hit Counter', 'Hard', 'Queue', 'Design a counter that returns hits received during the previous five minutes.', 'hit(1), hit(2), hit(300), getHits(300)', '3'),
    (91, 'Maximum Depth of Binary Tree', 'Easy', 'Trees', 'Return the maximum depth of a binary tree.', '[3,9,20,null,null,15,7]', '3'),
    (92, 'Same Tree', 'Easy', 'Trees', 'Determine whether two binary trees are structurally identical with equal values.', '[1,2,3], [1,2,3]', 'true'),
    (93, 'Invert Binary Tree', 'Easy', 'Trees', "Invert a binary tree by swapping every node's left and right children.", '[4,2,7,1,3,6,9]', '[4,7,2,9,6,3,1]'),
    (94, 'Symmetric Tree', 'Easy', 'Trees', 'Determine whether a binary tree is a mirror of itself.', '[1,2,2,3,4,4,3]', 'true'),
    (95, 'Binary Tree Level Order Traversal', 'Easy', 'Trees', 'Return the values of a binary tree level by level.', '[3,9,20,null,null,15,7]', '[[3],[9,20],[15,7]]'),
    (96, 'Validate Binary Search Tree', 'Medium', 'Trees', 'Determine whether a binary tree satisfies binary-search-tree ordering.', '[2,1,3]', 'true'),
    (97, 'Lowest Common Ancestor', 'Medium', 'Trees', 'Find the lowest common ancestor of two nodes in a binary tree.', 'root=[3,5,1,6,2,0,8], p=5, q=1', '3'),
    (98, 'Construct Binary Tree', 'Medium', 'Trees', 'Build a binary tree from preorder and inorder traversal arrays.', 'preorder=[3,9,20,15,7], inorder=[9,3,15,20,7]', '[3,9,20,null,null,15,7]'),
    (99, 'Binary Tree Right Side View', 'Medium', 'Trees', 'Return the nodes visible when looking at a binary tree from the right side.', '[1,2,3,null,5,null,4]', '[1,3,4]'),
    (100, 'Kth Smallest Element in BST', 'Medium', 'Trees', 'Return the kth smallest value in a binary search tree.', 'root=[3,1,4,null,2], k=1', '1'),
    (101, 'Binary Tree Maximum Path Sum', 'Hard', 'Trees', 'Find the maximum sum of any non-empty path in a binary tree.', '[-10,9,20,null,null,15,7]', '42'),
    (102, 'Serialize and Deserialize Binary Tree', 'Hard', 'Trees', 'Design algorithms to serialize and deserialize a binary tree.', '[1,2,3,null,null,4,5]', 'restored tree equals original'),
    (103, 'Recover Binary Search Tree', 'Hard', 'Trees', 'Recover a BST where exactly two node values were swapped.', '[3,1,4,null,null,2]', '[2,1,4,null,null,3]'),
    (104, 'Vertical Order Traversal', 'Hard', 'Trees', 'Return nodes grouped by vertical columns from left to right with required ordering.', '[3,9,20,null,null,15,7]', '[[9],[3,15],[20],[7]]'),
    (105, 'Count Complete Tree Nodes', 'Hard', 'Trees', 'Count the nodes of a complete binary tree efficiently.', '[1,2,3,4,5,6]', '6'),
    (106, 'Find if Path Exists', 'Easy', 'Graphs', 'Determine whether a path exists between two vertices in an undirected graph.', 'n=3, edges=[[0,1],[1,2]], source=0, destination=2', 'true'),
    (107, 'Flood Fill', 'Easy', 'Graphs', 'Replace the connected region containing a starting pixel with a new color.', 'image=[[1,1,1],[1,1,0],[1,0,1]], sr=1, sc=1, color=2', '[[2,2,2],[2,2,0],[2,0,1]]'),
    (108, 'Find the Town Judge', 'Easy', 'Graphs', 'Find the person trusted by everyone else and who trusts nobody.', 'n=3, trust=[[1,3],[2,3]]', '3'),
    (109, 'Find Center of Star Graph', 'Easy', 'Graphs', 'Find the center vertex of a star-shaped graph.', 'edges=[[1,2],[2,3],[4,2]]', '2'),
    (110, 'Number of Islands', 'Easy', 'Graphs', 'Count connected groups of land cells in a binary grid.', '[["1","1","0"],["1","0","0"],["0","0","1"]]', '2'),
    (111, 'Clone Graph', 'Medium', 'Graphs', 'Return a deep copy of a connected undirected graph.', 'adjList=[[2,4],[1,3],[2,4],[1,3]]', 'cloned graph'),
    (112, 'Course Schedule', 'Medium', 'Graphs', 'Determine whether all courses can be completed given prerequisite pairs.', 'numCourses=2, prerequisites=[[1,0]]', 'true'),
    (113, 'Rotting Oranges', 'Medium', 'Graphs', 'Use breadth-first search to determine when all reachable fresh oranges rot.', '[[2,1,1],[1,1,0],[0,1,1]]', '4'),
    (114, 'Pacific Atlantic Water Flow', 'Medium', 'Graphs', 'Find cells from which water can flow to both the Pacific and Atlantic oceans.', 'heights=[[1,2,2],[3,2,3],[2,4,5]]', '[[0,2],[1,0],[1,2],[2,1],[2,2]]'),
    (115, 'Number of Provinces', 'Medium', 'Graphs', 'Count connected components in a graph represented by an adjacency matrix.', 'isConnected=[[1,1,0],[1,1,0],[0,0,1]]', '2'),
    (116, 'Word Ladder', 'Hard', 'Graphs', 'Find the length of the shortest transformation sequence between two words.', 'begin="hit", end="cog", words=["hot","dot","dog","lot","log","cog"]', '5'),
    (117, 'Alien Dictionary', 'Hard', 'Graphs', 'Derive a valid character ordering from a sorted list of words in an alien language.', 'words=["wrt","wrf","er","ett","rftt"]', '"wertf"'),
    (118, 'Critical Connections', 'Hard', 'Graphs', 'Find edges whose removal disconnects an undirected network.', 'n=4, connections=[[0,1],[1,2],[2,0],[1,3]]', '[[1,3]]'),
    (119, 'Reconstruct Itinerary', 'Hard', 'Graphs', 'Reconstruct a lexicographically smallest itinerary using all flight tickets exactly once.', 'tickets=[["MUC","LHR"],["JFK","MUC"],["SFO","SJC"],["LHR","SFO"]]', '["JFK","MUC","LHR","SFO","SJC"]'),
    (120, 'Minimum Cost to Connect All Points', 'Hard', 'Graphs', 'Connect all points with minimum total Manhattan-distance edge cost.', 'points=[[0,0],[2,2],[3,10],[5,2],[7,0]]', '20'),
    (121, 'Climbing Stairs', 'Easy', 'Dynamic Programming', 'Count the distinct ways to climb n stairs using steps of one or two.', 'n=5', '8'),
    (122, 'Fibonacci Number', 'Easy', 'Dynamic Programming', 'Return the nth Fibonacci number.', 'n=6', '8'),
    (123, 'House Robber', 'Easy', 'Dynamic Programming', 'Maximize money robbed from houses without robbing adjacent houses.', '[2,7,9,3,1]', '12'),
    (124, 'Min Cost Climbing Stairs', 'Easy', 'Dynamic Programming', 'Find the minimum cost to reach the top when each step has a cost.', '[10,15,20]', '15'),
    (125, "Pascal's Triangle", 'Easy', 'Dynamic Programming', "Generate the first numRows of Pascal's triangle.", 'numRows=5', '[[1],[1,1],[1,2,1],[1,3,3,1],[1,4,6,4,1]]'),
    (126, 'Coin Change', 'Medium', 'Dynamic Programming', 'Find the minimum number of coins needed to make a target amount.', 'coins=[1,2,5], amount=11', '3'),
    (127, 'Longest Increasing Subsequence', 'Medium', 'Dynamic Programming', 'Find the length of the longest strictly increasing subsequence.', '[10,9,2,5,3,7,101,18]', '4'),
    (128, 'Unique Paths', 'Medium', 'Dynamic Programming', 'Count paths from the top-left to bottom-right of an m by n grid moving only right or down.', 'm=3, n=7', '28'),
    (129, 'Word Break', 'Medium', 'Dynamic Programming', 'Determine whether a string can be segmented into dictionary words.', 's="leetcode", wordDict=["leet","code"]', 'true'),
    (130, 'Partition Equal Subset Sum', 'Medium', 'Dynamic Programming', 'Determine whether an array can be partitioned into two subsets with equal sum.', '[1,5,11,5]', 'true'),
    (131, 'Edit Distance', 'Hard', 'Dynamic Programming', 'Find the minimum edits needed to transform one string into another.', 'word1="intention", word2="execution"', '5'),
    (132, 'Longest Common Subsequence', 'Hard', 'Dynamic Programming', 'Find the length of the longest subsequence common to two strings.', 'text1="abcde", text2="ace"', '3'),
    (133, 'Burst Balloons', 'Hard', 'Dynamic Programming', 'Choose an order to burst balloons to maximize the total coins collected.', '[3,1,5,8]', '167'),
    (134, 'Regular Expression Matching', 'Hard', 'Dynamic Programming', 'Determine whether a string matches a pattern containing . and *.', 's="aab", p="c*a*b"', 'true'),
    (135, 'Maximum Profit in Job Scheduling', 'Hard', 'Dynamic Programming', 'Choose non-overlapping jobs to maximize total profit.', 'start=[1,2,3,3], end=[3,4,5,6], profit=[50,10,40,70]', '120'),
]
