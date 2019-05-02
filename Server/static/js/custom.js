function writeDate(date) {
    document.write(`${fillWithZero(date.getDay(), 2)}.${fillWithZero(date.getMonth(), 2)}.${date.getFullYear()}`);
}

function getDate(date) {
    return `${date.getFullYear()}-${fillWithZero(date.getMonth(), 2)}-${fillWithZero(date.getDay(), 2)}`;
}

/* Fill numbers with zeros */
function fillWithZero(value, fill) {
    if (value < Math.pow(10, fill - 1)) {
        for (var i = 0; i < fill - 1; i++) {
            value = "0" + value;
        }
    }
    return value;
}