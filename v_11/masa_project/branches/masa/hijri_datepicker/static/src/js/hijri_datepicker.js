odoo.define('hijri_datepicker', function (require) {
"use strict"

var core = require('web.core');
var datepicker = require('web.datepicker');
var datetimefield = require('web.basic_fields');
var time = require('web.time');
var field_utils = require('web.field_utils');
var session = require('web.session');
var ListRenderer = require('web.ListRenderer');
var FormRenderer = require('web.FormRenderer');
var Session = require('web.Session');
var FIELD_CLASSES = {
    float: 'o_list_number',
    integer: 'o_list_number',
    monetary: 'o_list_number',
    text: 'o_list_text',
};

var DECORATIONS = [
    'decoration-bf',
    'decoration-it',
    'decoration-danger',
    'decoration-info',
    'decoration-muted',
    'decoration-primary',
    'decoration-success',
    'decoration-warning'
];

var _t = core._t;
var qweb = core.qweb;
var lang = '';
var date_format = '%d/%m/%Y';

    datepicker.DateWidget.include({
        start: function() {
            
            var def = new $.Deferred();
            var self = this;

            this.$input = this.$('input.oe_datepicker_master');
            this.$input_picker = this.$('input.oe_datepicker_container');
            this.$input_hijri = this.$el.find('input.oe_hijri');
            $(this.$input_hijri).val('');
            this._super();
            this.$input = this.$('input.oe_datepicker_master');

            function convert_to_hijri(date) {
            	if (date.length == 0) {
            		return false
            	}
            	var jd = $.calendars.instance('islamic').toJD(parseInt(date[0].year()),parseInt(date[0].month()),parseInt(date[0].day()));
                var date = $.calendars.instance('gregorian').fromJD(jd);
            	var date_value = new Date(parseInt(date.year()),parseInt(date.month())-1,parseInt(date.day()));
            	self.$el.find('input.oe_simple_date').val(self.formatClient(date_value, self.type_of_date));
            	self.change_datetime();
            }
            
            if($.ummalquraData != false){
                self._rpc({
                    model: 'res.users',
                    method: 'get_localisation',
                    args: [session.uid],
                }).then(function (res) {
                    def.resolve(res);
                });
                def.done(function(val) {
                    $(self.$input_hijri).calendarsPicker({
                        calendar: $.calendars.instance('islamic',val.lang),
                        dateFormat: 'M d, yyyy',
                        onSelect: convert_to_hijri,
                    });
                });
            }
            if($.ummalquraData == false){
                this._rpc({
                    model: 'date.log',
                    method: 'get_all_dates_dict',
                    args: [1],
                }).then(function (res) {
                    $.ummalquraData = res;
                    $.ummalquraDataOr = res;
                    //////////console.log($.ummalquraData);

                    self._rpc({
                        model: 'res.users',
                        method: 'get_localisation',
                        args: [session.uid],
                    }).then(function (res) {
                        def.resolve(res);
                    });
                    def.done(function(val) {
                        $(self.$input_hijri).calendarsPicker({
                            calendar: $.calendars.instance('islamic',val.lang),
                            dateFormat: 'M d, yyyy',
                            onSelect: convert_to_hijri,
                        });
                    });


                });
            }
    
            
           
            
            
            
        },
        formatClient: function (value, type) {
            if (type == 'datetime'){
                var date_format = time.getLangDatetimeFormat();
            }
            if (type == 'date'){
                var date_format = time.getLangDateFormat();
            }
            return moment(value).format(date_format);
        },
        convert_greg_to_hijri: function(text) {
            if (text) {
            	var cal_greg = $.calendars.instance('gregorian');
            	var cal_hijri = $.calendars.instance('islamic');
            	var text = text._i;
            	if (text.indexOf('-')!= -1){
                    var text_split = text.split('-');
                    
            		var year = parseInt(text_split[0]);
            		var month = parseInt(text_split[1]);
            		var day = parseInt(text_split[2]);
                    //console.log($.ummalquraData);
                    //console.log("..............text_split",year,month,day);

                    var jd = cal_greg.toJD(year,month,day);
                    //console.log("..............jd", jd);
                	var date = cal_hijri.fromJD(jd);
                	var m = (date.month() >=10 ? date.month():"0"+date.month());
                	var d = (date.day() >=10 ? date.day():"0"+date.day());
                	$(this.$input_hijri).val(cal_hijri.formatDate('M d, yyyy', date));
            	}

            	if(text.indexOf('/')!= -1){
            		var text_split = text.split('/');
            		var year = parseInt(text_split[2]);
            		var month = parseInt(text_split[1]);
            		var day = parseInt(text_split[0]);

            		var jd = cal_greg.toJD(year,month,day);
                	var date = cal_hijri.fromJD(jd);
                	var m = (date.month() >=10 ? date.month():"0"+date.month());
                	var d = (date.day() >=10 ? date.day():"0"+date.day());
                	$(this.$input_hijri).val(cal_hijri.formatDate('M d, yyyy', date));
            	}
            }
        },
        set_value_from_ui: function() {
            var value = this.$input.val() || false;
            this.value = this._parseClient(value);
            this.setValue(this.value);
            var fun = this.convert_greg_to_hijri;
            var value = this.value;
            var self = this;
            //console.log("....................value",value);
            if($.ummalquraData != false){
                this.convert_greg_to_hijri(this.value);
            }
            if($.ummalquraData == false){
                this._rpc({
                    model: 'date.log',
                    method: 'get_all_dates_dict',
                    args: [1],
                }).then(function (res) {
                    $.ummalquraData = res;
                    $.ummalquraDataOr = res;
                    self.convert_greg_to_hijri(self.value);
                });
            }


            
        },
        set_readonly: function(readonly) {
            this._super(readonly);
            this.$input_hijri.prop('readonly', this.readonly);
        },
        change_datetime: function(e) {
        	this._setValueFromUi();
        	this.trigger("datetime_changed");
        },
        changeDatetime: function () {
            if (this.isValid()) {
                var oldValue = this.getValue();
                this.set_value_from_ui();
                var newValue = this.getValue();

                if (!oldValue !== !newValue || oldValue && newValue && !oldValue.isSame(newValue)) {
                    // The condition is strangely written; this is because the
                    // values can be false/undefined
                    this.trigger("datetime_changed");
                }
            }
        },
    });

    datetimefield.FieldDate.include({
        start: function () {
            var self = this;
            this._super();
            var readonly = this.mode === 'readonly';
            var el = this.$el;
            if($.ummalquraData != false){
                if (readonly) {
                    var date_value = $(el).text();
                    ////console.log("............$(el)",$(el));
                    ////console.log("............date_value",date_value);
                    var hij_date = self.convert_greg_to_hijri(date_value)
                    el.append("<div><span class='oe_hijri'>"+hij_date+"</span></div>");
                }
                //return $.when(def, this._super.apply(this, arguments));
                return true;
            }
            if ($.ummalquraData == false){
                this._rpc({
                    model: 'date.log',
                    method: 'get_all_dates_dict',
                    args: [1],
                }).then(function (res) {
                    $.ummalquraData = res;
                    $.ummalquraDataOr = res;
                    //////////console.log($.ummalquraData);
                    if (readonly) {
                        var date_value = $(el).text();
                        ////console.log("............$(el)",$(el));
                        ////console.log("............date_value",date_value);
                        var hij_date = self.convert_greg_to_hijri(date_value)
                        el.append("<div><span class='oe_hijri'>"+hij_date+"</span></div>");
                    }
                    //return $.when(def, this._super.apply(this, arguments));
                    return true;
                    
    
    
                });
            }
            

        },
        
        convert_greg_to_hijri: function(text) {
            var numberMap = {
                '١': '1',
                '٢': '2',
                '٣': '3',
                '٤': '4',
                '٥': '5',
                '٦': '6',
                '٧': '7',
                '٨': '8',
                '٩': '9',
                '٠': '0'
            };

            text = text.replace(/[١٢٣٤٥٦٧٨٩٠]/g, function (match) {
                return numberMap[match];
            }).replace(/،/g, ',');

            ////console.log("...............text here", text);
            if (text) {
            	var cal_greg = $.calendars.instance('gregorian');
            	var cal_hijri = $.calendars.instance('islamic');
            	if (text.indexOf('-')!= -1){
            		var text_split = text.split('-');
            		var year = parseInt(text_split[0]);
            		var month = parseInt(text_split[1]);
            		var day = parseInt(text_split[2]);

                    ////console.log(".................year",year);
                    ////console.log(".................month",month);
                    ////console.log(".................day",day)

                    year = parseInt(year);
            		month = parseInt(month);
                    day = parseInt(day);

                    var jd = cal_greg.toJD(year,month,day);
                    jd = $.ummalquraData[year+'-'+month+'-'+day+'g'];
                    //////////console.log(".................jd1",jd);
                	var date = cal_hijri.fromJD(jd);
                	var m = (date.month() >=10 ? date.month():"0"+date.month());
                	var d = (date.day() >=10 ? date.day():"0"+date.day());
                	return cal_hijri.formatDate('M d, yyyy', date);
            	}

            	if(text.indexOf('/')!= -1){
            		var text_split = text.split('/');
            		var year = text_split[2];
            		var month = text_split[1];
            		var day = text_split[0];

                    ////console.log(".................2year",year);
                    ////console.log(".................2month",month);
                    ////console.log(".................2day",day);


                    year = parseInt(year);
            		month = parseInt(month);
                    day = parseInt(day);
                    
                    var jd = cal_greg.toJD(year,month,day);
                    jd = $.ummalquraData[year+'-'+month+'-'+day+'g'];
                    ////console.log(".................jd1",jd);

                	var date = cal_hijri.fromJD(jd);
                	var m = (date.month() >=10 ? date.month():"0"+date.month());
                	var d = (date.day() >=10 ? date.day():"0"+date.day());
                	return cal_hijri.formatDate('M d, yyyy', date);
            	}
            }
        },
    });

    ListRenderer.include({
        convert_greg_to_hijri: function(text) {
            var numberMap = {
                '١': '1',
                '٢': '2',
                '٣': '3',
                '٤': '4',
                '٥': '5',
                '٦': '6',
                '٧': '7',
                '٨': '8',
                '٩': '9',
                '٠': '0'
            };

            text = text.replace(/[١٢٣٤٥٦٧٨٩٠]/g, function (match) {
                return numberMap[match];
            }).replace(/،/g, ',');

            ////console.log("...............text here", text);
            if (text) {
            	var cal_greg = $.calendars.instance('gregorian');
            	var cal_hijri = $.calendars.instance('islamic');
            	if (text.indexOf('-')!= -1){
            		var text_split = text.split('-');
            		var year = parseInt(text_split[0]);
            		var month = parseInt(text_split[1]);
            		var day = parseInt(text_split[2]);

                    ////console.log(".................year",year);
                    ////console.log(".................month",month);
                    ////console.log(".................day",day)

                    year = parseInt(year);
            		month = parseInt(month);
                    day = parseInt(day);

                    var jd = cal_greg.toJD(year,month,day);
                    jd = $.ummalquraData[year+'-'+month+'-'+day+'g'];
                    //////////console.log(".................jd1",jd);
                	var date = cal_hijri.fromJD(jd);
                	var m = (date.month() >=10 ? date.month():"0"+date.month());
                	var d = (date.day() >=10 ? date.day():"0"+date.day());
                	return cal_hijri.formatDate('M d, yyyy', date);
            	}

            	if(text.indexOf('/')!= -1){
            		var text_split = text.split('/');
            		var year = text_split[2];
            		var month = text_split[1];
            		var day = text_split[0];

                    ////console.log(".................2year",year);
                    ////console.log(".................2month",month);
                    ////console.log(".................2day",day);


                    year = parseInt(year);
            		month = parseInt(month);
                    day = parseInt(day);
                    
                    var jd = cal_greg.toJD(year,month,day);
                    jd = $.ummalquraData[year+'-'+month+'-'+day+'g'];
                    ////console.log(".................jd1",jd);

                	var date = cal_hijri.fromJD(jd);
                	var m = (date.month() >=10 ? date.month():"0"+date.month());
                	var d = (date.day() >=10 ? date.day():"0"+date.day());
                	return cal_hijri.formatDate('M d, yyyy', date);
            	}
            }
        },

        _render: function () {
            var self = this;
            if ($.ummalquraData != false){
                var oldAllFieldWidgets = this.allFieldWidgets;
                this.allFieldWidgets = {}; // TODO maybe merging allFieldWidgets and allModifiersData into "nodesData" in some way could be great
                this.allModifiersData = [];
                return this._renderView().then(function () {
                    _.each(oldAllFieldWidgets, function (recordWidgets) {
                        _.each(recordWidgets, function (widget) {
                            widget.destroy();
                        });
                    });
                });
            }

            if ($.ummalquraData == false){
                self._rpc({
                    model: 'date.log',
                    method: 'get_all_dates_dict',
                    args: [1],
                }).then(function (res) {
                    $.ummalquraData = res;
                    $.ummalquraDataOr = res;

                    var oldAllFieldWidgets = self.allFieldWidgets;
                    self.allFieldWidgets = {}; // TODO maybe merging allFieldWidgets and allModifiersData into "nodesData" in some way could be great
                    self.allModifiersData = [];
                    return self._renderView().then(function () {
                        _.each(oldAllFieldWidgets, function (recordWidgets) {
                            _.each(recordWidgets, function (widget) {
                                widget.destroy();
                            });
                        });
                    });
                });
            }

        },

        
        
        
        _renderBodyCell: function (record, node, colIndex, options) {
            var tdClassName = 'o_data_cell';
            if (node.tag === 'button') {
                tdClassName += ' o_list_button';
            } else if (node.tag === 'field') {
                var typeClass = FIELD_CLASSES[this.state.fields[node.attrs.name].type];
                
                if (typeClass) {
                    tdClassName += (' ' + typeClass);
                }
                if (node.attrs.widget) {
                    tdClassName += (' o_' + node.attrs.widget + '_cell');
                }
            }
            var $td = $('<td>', {class: tdClassName});
    
            // We register modifiers on the <td> element so that it gets the correct
            // modifiers classes (for styling)
            var modifiers = this._registerModifiers(node, record, $td, _.pick(options, 'mode'));
            // If the invisible modifiers is true, the <td> element is left empty.
            // Indeed, if the modifiers was to change the whole cell would be
            // rerendered anyway.
            if (modifiers.invisible && !(options && options.renderInvisible)) {
                return $td;
            }
    
            if (node.tag === 'button') {
                return $td.append(this._renderButton(record, node));
            } else if (node.tag === 'widget') {
                return $td.append(this._renderWidget(record, node));
            }
            if (node.attrs.widget || (options && options.renderWidgets)) {
                var widget = this._renderFieldWidget(node, record, _.pick(options, 'mode'));
                this._handleAttributes(widget.$el, node);
                return $td.append(widget.$el);
            }
            var name = node.attrs.name;
            var field = this.state.fields[name];
            var value = record.data[name];
            var formattedValue = field_utils.format[field.type](value, field, {
                data: record.data,
                escape: true,
                isPassword: 'password' in node.attrs,
            });
            if(field.type == 'date' || field.type == 'datetime'){
                //console.log($.ummalquraData);
                var self = this;
                if ($.ummalquraData != false){
                    var dd = self.convert_greg_to_hijri(formattedValue);
                    if (formattedValue != false){
                        formattedValue += '</br>'+dd;
                    }

                    self._handleAttributes($td, node);
                    return $td.html(formattedValue);
                }

                if (false){
                    //console.log(this.state.fields[name]);
                    this._rpc({
                        model: 'date.log',
                        method: 'get_all_dates_dict',
                        args: [1],
                    }).then(function (res) {
                        $.ummalquraData = res;
                        $.ummalquraDataOr = res;
                        var dd = self.convert_greg_to_hijri(formattedValue);
                        if (dd != false){
                            formattedValue += '</br>'+dd;
                        }
                        
    
                        self._handleAttributes($td, node);
                        return $td.html(formattedValue);
    
                    });
                }
                
                
            }
            this._handleAttributes($td, node);
            return $td.html(formattedValue);
        }
    });

    FormRenderer.include({
        _render2: function () {
            var self = this;
            if ($.ummalquraData != false){
                var oldAllFieldWidgets = this.allFieldWidgets;
                this.allFieldWidgets = {}; // TODO maybe merging allFieldWidgets and allModifiersData into "nodesData" in some way could be great
                this.allModifiersData = [];
                return this._renderView().then(function () {
                    _.each(oldAllFieldWidgets, function (recordWidgets) {
                        _.each(recordWidgets, function (widget) {
                            widget.destroy();
                        });
                    });
                });
            }

            if ($.ummalquraData == false){
                self._rpc({
                    model: 'date.log',
                    method: 'get_all_dates_dict',
                    args: [1],
                }).then(function (res) {
                    $.ummalquraData = res;
                    $.ummalquraDataOr = res;

                    var oldAllFieldWidgets = self.allFieldWidgets;
                    self.allFieldWidgets = {}; // TODO maybe merging allFieldWidgets and allModifiersData into "nodesData" in some way could be great
                    self.allModifiersData = [];
                    return self._renderView().then(function () {
                        _.each(oldAllFieldWidgets, function (recordWidgets) {
                            _.each(recordWidgets, function (widget) {
                                widget.destroy();
                            });
                        });
                    });
                });
            }
        },
    });


    

});
