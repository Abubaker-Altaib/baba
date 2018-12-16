/* http://keith-wood.name/calendars.html
   Islamic calendar for jQuery v2.0.0.
   Written by Keith Wood (kbwood{at}iinet.com.au) August 2009.
   Available under the MIT (https://github.com/jquery/jquery/blob/master/MIT-LICENSE.txt) license. 
   Please attribute the author if you use it. */

(function($) { // Hide scope, no $ conflict

	/** Implementation of the Islamic or '16 civil' calendar.
		Based on code from <a href="http://www.iranchamber.com/calendar/converter/iranian_calendar_converter.php">http://www.iranchamber.com/calendar/converter/iranian_calendar_converter.php</a>.
		See also <a href="http://en.wikipedia.org/wiki/Islamic_calendar">http://en.wikipedia.org/wiki/Islamic_calendar</a>.
		@class IslamicCalendar
		@param [language=''] {string} The language code (default English) for localisation. */
	function IslamicCalendar(language) {
		this.local = this.regionalOptions[language || ''] || this.regionalOptions[''];
	}

	IslamicCalendar.prototype = new $.calendars.baseCalendar;

	$.extend(IslamicCalendar.prototype, {
		/** The calendar name.
			@memberof IslamicCalendar */
		name: 'Islamic',
		/** Julian date of start of Islamic epoch: 16 July 622 CE.
			@memberof IslamicCalendar */
		jdEpoch: 1948439.5,
		/** Days per month in a common year.
			@memberof IslamicCalendar */
		//daysPerMonth: [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29],
		/** <code>true</code> if has a year zero, <code>false</code> if not.
			@memberof IslamicCalendar */
		hasYearZero: false,
		/** The minimum month number.
			@memberof IslamicCalendar */
		minMonth: 1,
		/** The first month in the year.
			@memberof IslamicCalendar */
		firstMonth: 1,
		/** The minimum day number.
			@memberof IslamicCalendar */
		minDay: 1,

		/** Localisations for the plugin.
			Entries are objects indexed by the language code ('' being the default US/English).
			Each object has the following attributes.
			@memberof IslamicCalendar
			@property name {string} The calendar name.
			@property epochs {string[]} The epoch names.
			@property monthNames {string[]} The long names of the months of the year.
			@property monthNamesShort {string[]} The short names of the months of the year.
			@property dayNames {string[]} The long names of the days of the week.
			@property dayNamesShort {string[]} The short names of the days of the week.
			@property dayNamesMin {string[]} The minimal names of the days of the week.
			@property dateFormat {string} The date format for this calendar.
					See the options on <a href="BaseCalendar.html#formatDate"><code>formatDate</code></a> for details.
			@property firstDay {number} The number of the first day of the week, starting at 0.
			@property isRTL {number} <code>true</code> if this localisation reads right-to-left. */
		regionalOptions: { // Localisations
			'': {
				name: 'Islamic',
				epochs: ['BH', 'AH'],
				monthNames: ['Muharram', 'Safar', 'Rabi\' al-awwal', 'Rabi\' al-thani', 'Jumada al-awwal', 'Jumada al-thani',
				'Rajab', 'Sha\'aban', 'Ramadan', 'Shawwal', 'Dhu al-Qi\'dah', 'Dhu al-Hijjah'],
				monthNamesShort: ['محر', 'سفر', 'ربع1', 'ربع2', 'جمد1', 'جمد2', 'رجب', 'شعب', 'رمض', 'شوال', 'ذوقع', 'ذوحج'],
				dayNames: ['Yawm al-ahad', 'Yawm al-ithnayn', 'Yawm ath-thulaathaa\'',
				'Yawm al-arbi\'aa\'', 'Yawm al-khamīs', 'Yawm al-jum\'a', 'Yawm as-sabt'],
				dayNamesShort: ['Aha', 'Ith', 'Thu', 'Arb', 'Kha', 'Jum', 'Sab'],
				dayNamesMin: ['Ah','It','Th','Ar','Kh','Ju','Sa'],
				dateFormat: 'yyyy/mm/dd',
				firstDay: 6,
				isRTL: false
			}
		},

		/** Determine whether this date is in a leap year.
			@memberof IslamicCalendar
			@param year {CDate|number} The date to examine or the year to examine.
			@return {boolean} <code>true</code> if this is a leap year, <code>false</code> if not.
			@throws Error if an invalid year or a different calendar used. */
		leapYear: function(year) {
			var date = this._validate(year, this.minMonth, this.minDay, $.calendars.local.invalidYear);
			return (this.daysInYear(date.year()) === 355);
		},

		/** Determine the week of the year for a date.
			@memberof IslamicCalendar
			@param year {CDate|number} The date to examine or the year to examine.
			@param [month] {number} The month to examine.
			@param [day] {number} The day to examine.
			@return {number} The week of the year.
			@throws Error if an invalid date or a different calendar used. */
		weekOfYear: function(year, month, day) {
			// Find Sunday of this week starting on Sunday
			var checkDate = this.newDate(year, month, day);
			checkDate.add(-checkDate.dayOfWeek(), 'd');
			return Math.floor((checkDate.dayOfYear() - 1) / 7) + 1;
		},

		/** Retrieve the number of days in a year.
			@memberof IslamicCalendar
			@param year {CDate|number} The date to examine or the year to examine.
			@return {number} The number of days.
			@throws Error if an invalid year or a different calendar used. */
		daysInYear: function(year) {
			var daysCount = 0;
			for (var i = 1; i <= 12; i++) {
				daysCount += this.daysInMonth(year, i);
			}
			return daysCount;
		},

		/** Retrieve the number of days in a month.
			@memberof IslamicCalendar
			@param year {CDate|number} The date to examine or the year of the month.
			@param [month] {number} The month.
			@return {number} The number of days in this month.
			@throws Error if an invalid month/year or a different calendar used. */
		daysInMonth: function(year, month) {
			////////////console.log(year, month);
			/*var date = this._validate(year, month, this.minDay, $.calendars.local.invalidMonth);
			return this.daysPerMonth[date.month() - 1] +
				(date.month() === 12 && this.leapYear(date.year()) ? 1 : 0);*/
			var date = this._validate(year, month, this.minDay, $.calendars.local.invalidMonth);
			//var mcjdn = date.toJD() - 2400000 + 0.5; // Modified Chronological Julian Day Number (MCJDN)
			// the MCJDN's of the start of the lunations in the Umm al-Qura calendar are stored in the 'ummalquraData' array
			//var index = 0;
			// for (var i = 0; i < $.ummalquraData.length; i++) {
			// 	if ($.ummalquraData[i] > mcjdn) {
			// 		return ($.ummalquraData[index] - $.ummalquraData[index - 1]);
			// 	}
			// 	index++;
			// }
			if($.ummalquraData.hasOwnProperty(year+'-'+month+'-'+'30h')){
				//////////console.log("................hehe");
				return 30;
			}
			// $.each($.ummalquraData, function(key,value) {
			// 	if(key == year+'-'+month+'-'+'30h'){
			// 		return 30
			// 	}
			// });

			return 29; // Unknown outside
		},

		dayOfWeek: function(year, month, day) {
			//////////console.log(year, month, day) ;
			var date = this._validate(year, month, day,
				$.calendars.local.invalidDate || $.calendars.regionalOptions[''].invalidDate);
			
			var jd = this.toJD(date);

			//////////console.log("...........% this.daysInWeek().",jd) ;
			return this.g_week_day(jd);
			return (Math.floor(this.toJD(date)) + 2) % this.daysInWeek();
		},

		/** Determine whether this date is a week day.
			@memberof IslamicCalendar
			@param year {CDate|number} The date to examine or the year to examine.
			@param [month] {number} The month to examine.
			@param [day] {number} The day to examine.
			@return {boolean} <code>true</code> if a week day, <code>false</code> if not.
			@throws Error if an invalid date or a different calendar used. */
		weekDay: function(year, month, day) {
			return this.dayOfWeek(year, month, day) !== 5;
		},

		/** Retrieve the Julian date equivalent for this date,
			i.e. days since January 1, 4713 BCE Greenwich noon.
			@memberof IslamicCalendar
			@param year {CDate|number} The date to convert or the year to convert.
			@param [month] {number} The month to convert.
			@param [day] {number} The day to convert.
			@return {number} The equivalent Julian date.
			@throws Error if an invalid date or a different calendar used. */
		toJD: function(year, month, day) {
			//////////console.log('0000000000000',year, month, day);
			////////////console.log('1111111111111',$.ummalquraData[year+'-'+month+'-'+day+'h']);
			////////////console.log('1111111111111',$.ummalquraData);
			var date = this._validate(year, month, day, $.calendars.local.invalidDate);
			
			year = date.year();
			month = date.month();
			day = date.day();
			////////console.log("11111111111111111111",year, month, day);
			////////////console.log("11111111111111111111",$.ummalquraDataOr);
			////////console.log($.ummalquraData[year+'-'+month+'-'+day+'h']);
			return $.ummalquraData[year+'-'+month+'-'+day+'h'];

			var val = '';
			$.each($.ummalquraData, function(key,value) {
				if(key == date.year()+'-'+date.month()+'-'+date.day()+'h'){
					val = value;
				}
			});
			
			return val;
			return $.ummalquraData[year+'-'+month+'-'+day+'h'];
			var index = (12 * (date.year() - 1)) + date.month() - 15292;
			var mcjdn = date.day() + $.ummalquraData[index - 1] - 1;
			return mcjdn + 2400000 - 0.5;
		},

		/** Create a new date from a Julian date.
			@memberof IslamicCalendar
			@param jd {number} The Julian date to convert.
			@return {CDate} The equivalent date. */
		fromJD: function(jd) {
			////////console.log(".................jd",jd);
			
			
			//var mcjdn = jd - 2400000 + 0.5; // Modified Chronological Julian Day Number (MCJDN)
			// the MCJDN's of the start of the lunations in the Umm al-Qura calendar 
			// are stored in the 'ummalquraData' array
			var val = '';
			$.each($.ummalquraData, function(key,value) {
				if(value == jd && key[key.length -1] == 'h'){
					val = key;
				}
			  }); 
			// var index = 0;
			// for (var i = 0; i < $.ummalquraData.length; i++) {
			// 	if ($.ummalquraData[i] > mcjdn) {
			// 		break;
			// 	}
			// 	index++;
			// }
			// var lunation = index + 15292; //UmmAlQura Lunation Number
			// var ii = Math.floor((lunation - 1) / 12);
			// var year = ii + 1;
			// var month = lunation - 12 * ii;
			// var day = mcjdn - $.ummalquraData[index - 1] + 1;
			
			var text_split = val.split('-');
			////////////console.log(".................text_split",text_split);
			var year = parseInt(text_split[0]);
			var month = parseInt(text_split[1]);
			var day = parseInt(text_split[2]);
			return this.newDate(year, month, day);
		}

	});

	// Islamic (16 civil) calendar implementation
	$.calendars.calendars.islamic = IslamicCalendar;

	$.ummalquraData = false;

})(jQuery);
