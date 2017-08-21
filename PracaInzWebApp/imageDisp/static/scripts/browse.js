/**
 * Created by Bartosz on 8/15/2017.
 */
function checkKey(e) {

    e = e || window.event;
    console.log(e.keyCode);
    if (e.keyCode == '37') {
       goLeft();

    }
    else if (e.keyCode == '39') {
       goRight();

    }

}
function goLeft() {
    num = num - 1;
    console.log(num);
    window.location.href  = "/gallery/browse/".concat(num.toString());
}
function goRight() {
    num = num + 1;
    console.log(num);
    window.location.href  = "/gallery/browse/".concat(num.toString());
}
document.onkeydown = checkKey;