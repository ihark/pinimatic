$(document).ready(
	alertFade()
);

function alertFade() {
    var delayTime  = 3000,
        fades     = $('.alert.fade');
		clicks     = $('.alert.click');

    delayTime = delayTime + (fades.length * 250);

    fades.each(function() {
        $(this).delay(delayTime).fadeOut('slow');
        delayTime -= 250;
    });
	clicks.each(function() {
        $(this).append('<span class="close">X</span>');
        delayTime -= 250;
    });
	
}