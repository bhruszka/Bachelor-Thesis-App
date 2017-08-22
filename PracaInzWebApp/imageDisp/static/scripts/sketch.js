var canvas;
var clicked_circle;
var which;
var radius = 25;
var first_time = true;
// var path = "";

function draw_me(name ,point){
    fill(255, 0, 0);
    line(point.y1, point.x1, point.y2, point.x2);
    ellipse(point.y1, point.x1, radius, radius);
    ellipse(point.y2, point.x2, radius, radius);

    fill(255);
    textSize(11);
    textAlign(CENTER, CENTER);
    text(name, point.y1, point.x1);
    text(name, point.y2, point.x2);
}

function  check_point_collision(point){
  print(point);
  print(mouseX);
  print(mouseY);
  if(dist(mouseX, mouseY, point.y1, point.x1) < radius){
      return 0;
  }
  if(dist(mouseX, mouseY, point.y2, point.x2) < radius){
    return 1;
  }
  return -1;
}
function post_teeth_data() {
    document.getElementById("submit").disabled = true;
    document.getElementById("reset").disabled = true;
    document.getElementById("fullreset").disabled = true;

    var form = document.getElementById('teeth_form');
    form.setAttribute("method", "post");
    // form.setAttribute("action", path);

    for(var key in teeth_data) {
        if(teeth_data.hasOwnProperty(key)) {
            var hiddenFieldX1 = document.createElement("input");
            hiddenFieldX1.setAttribute("type", "hidden");
            hiddenFieldX1.setAttribute("name", key + "X1");
            hiddenFieldX1.setAttribute("value", teeth_data[key].x1);

            var hiddenFieldY1 = document.createElement("input");
            hiddenFieldY1.setAttribute("type", "hidden");
            hiddenFieldY1.setAttribute("name", key + "Y1");
            hiddenFieldY1.setAttribute("value", teeth_data[key].y1);

            var hiddenFieldX2 = document.createElement("input");
            hiddenFieldX2.setAttribute("type", "hidden");
            hiddenFieldX2.setAttribute("name", key + "X2");
            hiddenFieldX2.setAttribute("value", teeth_data[key].x2);

            var hiddenFieldY2 = document.createElement("input");
            hiddenFieldY2.setAttribute("type", "hidden");
            hiddenFieldY2.setAttribute("name", key + "Y2");
            hiddenFieldY2.setAttribute("value", teeth_data[key].y2);

            form.appendChild(hiddenFieldX1);
            form.appendChild(hiddenFieldY1);
            form.appendChild(hiddenFieldX2);
            form.appendChild(hiddenFieldY2);
         }
    }

    document.body.appendChild(form);
    form.submit();
}

function centerCanvas() {
  var image = document.getElementById('mainimage');
  var rect = image.getBoundingClientRect();
  canvas.position(image.offsetLeft, image.offsetTop);
}
function setup() {
  image = document.getElementById('mainimage');
  var rect = image.getBoundingClientRect();
  canvas = createCanvas(rect.width, rect.height);
  centerCanvas();
  frameRate(30);
  // noLoop();
  for (var key in teeth_data) {
      print(teeth_data[key]);
  }
}

function draw() {
  centerCanvas();
  // print(clicked_circle);
  // print(which);
  if((!mouseIsPressed || which < 0) && !first_time){
    return;
  }
  clear();
  // print(clicked_circle);
  if (clicked_circle && which >= 0) {

    if(which === 0){
      teeth_data[clicked_circle].y1 = mouseX;
      teeth_data[clicked_circle].x1 = mouseY;
    }
    else{
      teeth_data[clicked_circle].y2 = mouseX;
      teeth_data[clicked_circle].x2 = mouseY;
    }
  }
  for (var key in teeth_data) {
      draw_me(key, teeth_data[key]);
  }
  first_time = false;
}
function mousePressed() {
  for (var key in teeth_data) {
      which = check_point_collision(teeth_data[key]);
      if(which >= 0 ){
        clicked_circle = key;
        print(key);
        return;
      }
  }
  print("presed");
}
function mouseReleased() {
  print("released");
  clicked_circle = null;
  which = -1;
}
function windowResized() {
  centerCanvas();
}

function reset(){
    window.location.reload(false);
    return;
}

function full_reset() {
  return;
}
