/* Global variables and structures */
var item = $(".timeout");
var seconds = item.attr("seconds");
var interval, timeout;

/* Define differentsession options */
if (seconds > 0) {
    item.attr("data-content", "Zur Sicherheit Ihrer Daten wird die Sitzung nach o.g. Zeit automatisch beendet und Sie werden abgemeldet. Sie können die Zeit jederzeit durch Klicken verlängern.");
    setTime();
} else {
    $("#timeout-time").text("Lifetime");
    item.attr("data-content", "Die automatische Abmeldung wurde durch Sie bei der Anmeldung deaktiviert! Die Sitzung wird erst geschlossen, wenn Sie sich manuell abmelden.");
}

/* Hover effects */
$(".timeout").hover(function () {
    $(".spinner").toggleClass("hovered");
});

$(".timeout").mouseover(function () {
    $(".timeout").popover("show");
});

$(".timeout").mouseout(function () {
    $(".timeout").popover("hide");
});

/* Fill time integers with zeros */
function fillZero(v) {
    return v < 10 ? "0" + v : v;
}

/* Restart counter and refresh session */
if (seconds > 0) {
    $(".timeout").on("click", function () {
        $.ajax({
            url: "/sessionrefresh",
            success: function (result) {
                console.log(result);
                setTime();
            }
        });
    });
}

/* Initialize timer interation */
function setTime() {
    clearInterval(interval);
    clearTimeout(timeout);

    var now = new Date().getTime();
    var difference = now + seconds * 1000 - now;
    difference = countdown("#timeout-time", difference);

    /* Refresh every second */
    interval = setInterval(function () {
        if (difference >= 0) {
            difference = countdown("#timeout-time", difference);
        } else {
            clearInterval(interval);
        }
    }, 1000);

    /* Redirect after timeout */
    timeout = setTimeout(function () {
        window.location = "/logout";
    }, seconds * 1000);
}

/* Calculate the countdown and print remaining time */
function countdown(element, difference) {
    /* Time calculations for days, hours, minutes and seconds */
    var days = Math.floor(difference / (1000 * 60 * 60 * 24));
    var hours = fillZero(Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)));
    var minutes = fillZero(Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60)));
    var seconds = fillZero(Math.floor((difference % (1000 * 60)) / 1000));

    /* Display the result in the selected element */
    if (hours <= 0 && days <= 0) {
        $(element).text(`${minutes}:${seconds}`);
    } else if (days <= 0) {
        $(element).text(`${hours}:${minutes}:${seconds}`);
    } else {
        $(element).text(`${days}T ${hours}:${minutes}:${seconds}`);
    }

    /* Subtracts every second from the remaining milliseconds */
    difference -= 1000;

    return difference;
}