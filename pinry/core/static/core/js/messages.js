$(document).ready(
	alertFade()
);

function alertFade() {
    var delayTime  = 3000,
        alerts     = $('.alert');

    delayTime = delayTime + (alerts.length * 250);

    alerts.each(function() {
        $(this).delay(delayTime).fadeOut('slow');
        delayTime -= 250;
    });
}