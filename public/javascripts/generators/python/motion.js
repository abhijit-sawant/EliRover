'use strict';

//goog.provide('Blockly.Python.logic');

goog.require('Blockly.Python');

Blockly.Python['motion_forward'] = function(block) {
  // TODO: Assemble Python into code variable.
  var code = 'forward()\n';
  return code;
};

Blockly.Python['motion_sleep'] = function(block) {
  var number_seconds = block.getFieldValue('seconds');
  // TODO: Assemble Python into code variable.
  var code = 'time.sleep(' + number_seconds.toString() + ')';
  return code;
};
