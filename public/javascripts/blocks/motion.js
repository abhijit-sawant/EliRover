'use strict';

//goog.provide('Blockly.Blocks.motion');  // Deprecated
//goog.provide('Blockly.Constants.Logic');

goog.require('Blockly.Blocks');
goog.require('Blockly');

/**
 * Unused constant for the common HSV hue for all blocks in this category.
 * @deprecated Use Blockly.Msg['LOGIC_HUE']. (2018 April 5)
 */
//Blockly.Constants.Logic.HUE = 210;

Blockly.defineBlocksWithJsonArray([ 
	{
	  "type": "motion_forward",
	  "message0": "Forward",
	  "previousStatement": null,
	  "nextStatement": null,
	  "colour": 0,
	  "tooltip": "%{BKY_MOTION_FORWARD_TOOLTIP}",
	  "helpUrl": ""
	},
	{
		"type": "motion_backward",
		"message0": "Backward",
		"previousStatement": null,
		"nextStatement": null,
		"colour": 0,
		"tooltip": "%{BKY_MOTION_BACKWARD_TOOLTIP}",
		"helpUrl": ""
	},	
	{
		"type": "motion_turn_right",
		"message0": "Turn Right",
		"previousStatement": null,
		"nextStatement": null,
		"colour": 0,
		"tooltip": "%{BKY_MOTION_TURN_RIGHT_TOOLTIP}",
		"helpUrl": ""
	},	
	{
		"type": "motion_turn_left",
		"message0": "Turn Left",
		"previousStatement": null,
		"nextStatement": null,
		"colour": 0,
		"tooltip": "%{BKY_MOTION_TURN_LEFT_TOOLTIP}",
		"helpUrl": ""
	},	
	{
	  "type": "motion_stop",
	  "message0": "Stop",
	  "previousStatement": null,
	  "nextStatement": null,
	  "colour": 0,
	  "tooltip": "%{BKY_MOTION_STOP_TOOLTIP}",
	  "helpUrl": ""
	},	
	{
	  "type": "motion_sleep",
	  "message0": "Keep doing for %1 seconds",
	  "colour": 0,
	  "args0": [
	    {
	      "type": "field_number",
	      "name": "seconds",
	      "value": 1,
	      "precision": 1
	    }
	  ],
	  "previousStatement": null,
	  "nextStatement": null,
	  "tooltip": "%{BKY_MOTION_SLEEP_TOOLTIP}",
	  "helpUrl": ""
	}  	
]);
