$(document).ready(
	alertFade()
);

function alertFade() {
    var delayTime  = 3000,
        fades     = $('.alert.fade-out');

    delayTime = delayTime + (fades.length * 250);

    fades.each(function() {
        $(this).delay(delayTime).fadeOut('slow');
        delayTime -= 250;
    });
}