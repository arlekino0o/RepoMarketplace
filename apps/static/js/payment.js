class PaymentForm {

    constructor() {

        this.number =
            document.querySelector(
                "[name=card_number]"
            );

        this.owner =
            document.querySelector(
                "[name=card_name]"
            );

        this.expire =
            document.querySelector(
                "[name=expire]"
            );

        this.cvv =
            document.querySelector(
                "[name=cvv]"
            );

        this.init();

    }

    init() {

        if (!this.number) {
            return;
        }

        this.number.addEventListener(
            "input",
            this.formatNumber
        );

        this.expire.addEventListener(
            "input",
            this.formatExpire
        );

        this.cvv.addEventListener(
            "input",
            this.limitCVV
        );

    }

    formatNumber(event) {

        let value =
            event.target.value.replace(/\D/g, "");

        value =
            value.match(/.{1,4}/g)?.join(" ") || "";

        event.target.value = value;

    }

    formatExpire(event) {

        let value =
            event.target.value.replace(/\D/g, "");

        if (value.length > 2) {

            value =
                value.slice(0, 2) +
                "/" +
                value.slice(2, 4);

        }

        event.target.value = value;

    }

    limitCVV(event) {

        event.target.value =
            event.target.value
                .replace(/\D/g, "")
                .slice(0, 3);

    }

}

document.addEventListener(
    "DOMContentLoaded",
    () => new PaymentForm()
);