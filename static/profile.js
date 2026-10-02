/* =====================================================
   CODEMASTER PROFILE JAVASCRIPT
===================================================== */

document.addEventListener("DOMContentLoaded", function() {


    // =================================================
    // GET ELEMENTS
    // =================================================

    const editButton =
        document.getElementById("openEditProfile");

    const editModal =
        document.getElementById("editModal");

    const closeButton =
        document.getElementById("closeEditProfile");

    const cancelButton =
        document.getElementById("cancelEdit");

    const imageInput =
        document.getElementById("profile_image");

    const editPreview =
        document.getElementById("editPreview");


    // =================================================
    // OPEN EDIT PROFILE
    // =================================================

    if (editButton) {

        editButton.addEventListener("click", function() {

            editModal.classList.add("show");

            document.body.style.overflow = "hidden";

        });

    }


    // =================================================
    // CLOSE MODAL
    // =================================================

    function closeModal() {

        editModal.classList.remove("show");

        document.body.style.overflow = "";

    }


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeModal
        );

    }


    if (cancelButton) {

        cancelButton.addEventListener(
            "click",
            closeModal
        );

    }


    // =================================================
    // CLOSE WHEN CLICKING OUTSIDE
    // =================================================

    if (editModal) {

        editModal.addEventListener(
            "click",
            function(event) {

                if (event.target === editModal) {

                    closeModal();

                }

            }
        );

    }


    // =================================================
    // ESC KEY CLOSE
    // =================================================

    document.addEventListener(
        "keydown",
        function(event) {

            if (
                event.key === "Escape" &&
                editModal.classList.contains("show")
            ) {

                closeModal();

            }

        }
    );


    // =================================================
    // PROFILE IMAGE PREVIEW
    // =================================================

    if (imageInput) {

        imageInput.addEventListener(
            "change",
            function() {

                const file = this.files[0];

                if (!file) {
                    return;
                }


                // Check image type

                if (!file.type.startsWith("image/")) {

                    alert("Please select a valid image.");

                    this.value = "";

                    return;

                }


                // Maximum 5 MB

                if (file.size > 5 * 1024 * 1024) {

                    alert(
                        "Profile image must be less than 5 MB."
                    );

                    this.value = "";

                    return;

                }


                const reader =
                    new FileReader();


                reader.onload =
                    function(event) {

                        if (
                            editPreview.tagName === "IMG"
                        ) {

                            editPreview.src =
                                event.target.result;

                        } else {

                            const img =
                                document.createElement("img");

                            img.src =
                                event.target.result;

                            img.alt =
                                "Profile";

                            editPreview.replaceWith(img);

                            img.id =
                                "editPreview";

                        }

                    };


                reader.readAsDataURL(file);

            }
        );

    }


    // =================================================
    // FORM SUBMIT
    // =================================================

    const form =
        document.getElementById("editProfileForm");


    if (form) {

        form.addEventListener(
            "submit",
            function() {

                const saveButton =
                    form.querySelector(".save-btn");


                if (saveButton) {

                    saveButton.innerHTML =
                        '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';

                    saveButton.disabled = true;

                }

            }
        );

    }


});