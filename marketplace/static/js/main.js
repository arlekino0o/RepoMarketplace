document.addEventListener(
    "DOMContentLoaded",
    () => {

        document
            .querySelectorAll(".alert")
            .forEach(alert => {

                setTimeout(() => {

                    alert.style.transition =
                        ".3s";

                    alert.style.opacity = "0";

                    alert.style.transform =
                        "translateY(-10px)";

                    setTimeout(
                        () => alert.remove(),
                        300
                    );

                }, 4000);

            });

        document
            .querySelectorAll("[data-confirm]")
            .forEach(button => {

                button.addEventListener(
                    "click",
                    event => {

                        if (
                            !confirm(
                                button.dataset.confirm
                            )
                        ) {

                            event.preventDefault();

                        }

                    }
                );

            });

    }
);
