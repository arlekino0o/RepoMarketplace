class FormManager {

    constructor() {

        this.forms = document.querySelectorAll("form");

        this.init();

    }

    init() {

        this.forms.forEach(form => {

            this.prepareInputs(form);
            this.preventDoubleSubmit(form);

        });

    }

    prepareInputs(form) {

        const fields = form.querySelectorAll(
            "input, textarea, select"
        );

        fields.forEach(field => {

            field.classList.add("form-control");

            field.addEventListener(
                "focus",
                () => {

                    field.classList.remove("is-invalid");

                }
            );

            field.addEventListener(
                "blur",
                () => {

                    this.validate(field);

                }
            );

        });

    }

    validate(field) {

        if (field.hasAttribute("required")) {

            if (!field.value.trim()) {

                field.classList.add("is-invalid");
                field.classList.remove("is-valid");

                return false;

            }

        }

        if (field.type === "email") {

            const regex =
                /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (
                field.value &&
                !regex.test(field.value)
            ) {

                field.classList.add("is-invalid");

                return false;

            }

        }

        field.classList.remove("is-invalid");
        field.classList.add("is-valid");

        return true;

    }

    preventDoubleSubmit(form) {

        form.addEventListener(
            "submit",
            () => {

                const button =
                    form.querySelector(
                        "[type=submit]"
                    );

                if (!button) {
                    return;
                }

                button.disabled = true;

                button.dataset.original =
                    button.innerHTML;

                button.innerHTML =
                    "Загрузка...";

                setTimeout(() => {

                    button.disabled = false;

                    button.innerHTML =
                        button.dataset.original;

                }, 5000);

            }
        );

    }

}

document.addEventListener(
    "DOMContentLoaded",
    () => new FormManager()
);
