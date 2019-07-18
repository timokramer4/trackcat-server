/* Initialize the live validation */
function initializeValidation(formName) {
    var allInputs = document.forms[formName].getElementsByTagName("input");
    var submitBtn = $("#" + formName).find(":button");
    for (var i = 0; i < allInputs.length; i++) {
        var item = allInputs[i];
        if (item.getAttribute("validate") != null || item.getAttribute("validate") || (item.getAttribute("validateNewPass") > 0 && item.getAttribute("validateNewPass") <= 2)) {
            item.addEventListener("input", function () {
                if (validate(allInputs)) {
                    submitBtn[0].disabled = false;
                } else {
                    submitBtn[0].disabled = true;
                }
            });
        }
    }
}

/* Validate function */
function validate(allInputs) {
    var emailPattern = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    var passwordPattern = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])(?!.*\s).{8,15}$/;
    var namePattern = /^[A-Z](((\-|\s)[A-ZÄÖÜ])?[a-zäöüß]*)*$/;
    var datePattern = /^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$/;

    var result = true;

    for (var i = 0; i < allInputs.length; i++) {
        var item = allInputs[i];
        if (item.getAttribute("validate") != null || item.getAttribute("validate") || (item.getAttribute("validateNewPass") > 0 && item.getAttribute("validateNewPass") <= 2)) {
            if (item.value == null) {
                markField(item, false);
                result = false;
            } else if (item.value.length > 0 || item.type.toLocaleLowerCase() == "date") {
                if (item.type.toLocaleLowerCase() == "password") {
                    if (item.getAttribute("validateNewPass") != null) {
                        var pass1 = $('[validateNewPass="1"]');

                        if (item.getAttribute("validateNewPass") == 1) {
                            if (item.value.match(passwordPattern)) {
                                markField(item, true);
                                setHint(item, false);
                            } else {
                                markField(item, false);
                                setHint(item, true, "Das Passwort wird von unserem System nicht unterstützt: Das Passwort muss zwischen 8 und 15 Zeichen lang sein und mindestens folgende Parameter enthalten: 1x Groß- und Kleinbuchstabe, 1x Zahl und 1x Sonderzeichen");
                                result = false;
                            }
                        } else {
                            if (item.value == pass1[0].value) {
                                markField(item, true);
                                setHint(item, false);
                            } else {
                                markField(item, false);
                                setHint(item, true, "Die Passwörter stimmen nicht überein!");
                                result = false;
                            }
                        }
                    } else {
                        if (item.value.match(passwordPattern)) {
                            markField(item, true);
                            setHint(item, false);
                        } else {
                            markField(item, false);
                            setHint(item, true, "Das Passwort wird von unserem System nicht unterstützt: Das Passwort muss zwischen 8 und 15 Zeichen lang sein und mindestens folgende Parameter enthalten: 1x Groß- und Kleinbuchstabe, 1x Zahl und 1x Sonderzeichen");
                            result = false;
                        }
                    }
                } else if (item.type.toLocaleLowerCase() == "email") {
                    if (item.value.match(emailPattern)) {
                        markField(item, true);
                        setHint(item, false);
                    } else {
                        markField(item, false);
                        setHint(item, true, "Bitte kontrolliere deine E-Mail Adresse, sie entspricht keinem gültigen E-Mail Format!");
                        result = false;
                    }
                } else if (item.type.toLocaleLowerCase() == "text") {
                    if (item.value.match(namePattern)) {
                        markField(item, true);
                        setHint(item, false);
                    } else {
                        markField(item, false);
                        setHint(item, true, "Der eingegebene Name entspricht keinem gültigen Format!");
                        result = false;
                    }
                } else if (item.type.toLocaleLowerCase() == "date") {
                    var unixToday = new Date().getTime() / 1000;
                    var unixSelected = new Date(item.value).getTime() / 1000;
                    if (item.value.match(datePattern)) {
                        if (unixSelected > unixToday) {
                            markField(item, false);
                            setHint(item, true, "Sie sind noch nicht geboren, das könnte schwierig werden!");
                            result = false;
                        } else {
                            markField(item, true);
                            setHint(item, false);
                            result = true;
                        }
                    } else {
                        markField(item, false);
                        setHint(item, true, "Bitte geben Sie ein gültiges Geburtsdatum ein!");
                        result = false;
                    }
                } else if (item.type.toLocaleLowerCase() == "checkbox") {
                    if (item.checked == true) {
                        markField(item, null);
                    } else {
                        markField(item, false);
                        result = false;
                    }
                } else if (item.type.toLocaleLowerCase() == "radio") {
                    var parent = $(item).closest("div.form-group");
                    var radios = $(parent).find(":radio");

                    /* Check all radio boxes */
                    var checkedRadio = false;
                    for (var j = 0; j < radios.length; j++) {
                        var radio = radios[j];

                        if (radio.checked == true) {
                            checkedRadio = true;
                        }
                    }

                    /* Mark or demark radios based on result */
                    for (var j = 0; j < radios.length; j++) {
                        var radio = radios[j];

                        if (checkedRadio) {
                            markField(radio, null);
                        } else {
                            markField(radio, false);
                            result = false;
                        }
                    }
                }
            } else {
                markField(item);
                setHint(item, false);
                result = false;
            }

        }
    }
    return result;
}

/* Mark valid and invalid fields */
function markField(field, value) {
    if (value == null) {
        field.classList.remove("is-valid");
        field.classList.remove("text-red");
        field.classList.remove("is-invalid");
        field.classList.remove("text-green");
    } else {
        if (value) {
            field.classList.remove("is-invalid");
            field.classList.remove("text-red");
            field.classList.add("is-valid");
            field.classList.add("text-green");
        } else if (!value) {
            field.classList.remove("is-valid");
            field.classList.remove("text-green");
            field.classList.add("is-invalid");
            field.classList.add("text-red");
        }
    }
}

/* Set hint message if invalid input */
function setHint(inputField, show, msg) {
    var hintName = "hint_" + inputField.id;
    if (show) {
        var hint = document.createElement("small");
        hint.id = hintName;
        hint.className = "form-text text-muted ml-3 hint";
        hint.innerText = msg;
        if (document.getElementById(hintName) == null) {
            inputField.parentNode.appendChild(hint);
        }
    } else {
        if (document.getElementById(hintName) != null) {
            document.getElementById(hintName).remove();
        }
    }
}