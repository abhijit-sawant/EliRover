'use strict';

//goog.provide('Blockly.Python.logic');

goog.require('Blockly.Python');

Blockly.Python['motion_forward'] = function(block) {
  // TODO: Assemble Python into code variable.
  var code = 'rover.move_forward()\n';
  return code;
};

Blockly.Python['motion_backward'] = function(block) {
  var code = 'rover.move_backward()\n';
  return code;
};

Blockly.Python['motion_turn_right'] = function(block) {
  var code = 'rover.turn_right()\n';
  return code;
};

Blockly.Python['motion_turn_left'] = function(block) {
  var code = 'rover.turn_left()\n';
  return code;
};

Blockly.Python['motion_stop'] = function(block) {
  var code = 'rover.stop()\n';
  return code;
};

Blockly.Python['motion_sleep'] = function(block) {
  var number_seconds = block.getFieldValue('seconds');
  var code = 'time.sleep(' + number_seconds.toString() + ')\n';
  code += 'rover.stop()\n';
  return code;
};
