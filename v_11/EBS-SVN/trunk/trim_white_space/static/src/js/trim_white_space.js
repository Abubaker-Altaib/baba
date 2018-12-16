odoo.define('trim_white_space', function (require){
"use strict";
var ajax = require('web.ajax');
var field_utils = require('web.field_utils');
var Widget = require('web.Widget');
// require original module JS
var AbstractFields = require('web.AbstractField');

AbstractFields.include({
    _setValue: function (value, options) {
        // we try to avoid doing useless work, if the value given has not
        // changed.  Note that we compare the unparsed values.
        if (this.lastSetValue === value || (this.value === false && value === '')) {
            return $.when();
        }
        this.lastSetValue = value;
        if(typeof value=='string')
        {
            value=value.trim()
        }
        try {
            value = this._parseValue(value);
            this._isValid = true;
        } catch (e) {
            this._isValid = false;
            this.trigger_up('set_dirty', {dataPointID: this.dataPointID});
            return $.Deferred().reject();
        }
        if (!(options && options.forceChange) && this._isSameValue(value)) {
            return $.when();
        }
        var def = $.Deferred();
        var changes = {};
        changes[this.name] = value;
        this.trigger_up('field_changed', {
            dataPointID: this.dataPointID,
            changes: changes,
            viewType: this.viewType,
            doNotSetDirty: options && options.doNotSetDirty,
            onSuccess: def.resolve.bind(def),
            onFailure: def.reject.bind(def),
        });
        return def;
    },
 });

});

