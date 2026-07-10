class Navbar {

    constructor() {

        this.button = document.getElementById("menuToggle");
        this.menu = document.getElementById("navLinks");

        this.init();

    }

    init() {

        if (!this.button || !this.menu) {
            return;
        }

        this.button.addEventListener(
            "click",
            () => this.toggle()
        );

        document.addEventListener(
            "click",
            (event) => {

                if (
                    !this.menu.contains(event.target) &&
                    !this.button.contains(event.target)
                ) {
                    this.close();
                }

            }
        );

        window.addEventListener(
            "resize",
            () => {

                if (window.innerWidth > 768) {
                    this.close();
                }

            }
        );

    }

    toggle() {

        this.menu.classList.toggle("active");

    }

    close() {

        this.menu.classList.remove("active");

    }

}

document.addEventListener(
    "DOMContentLoaded",
    () => new Navbar()
);