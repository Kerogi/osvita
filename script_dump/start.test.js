	                this.props.isHeadDc
	                    ? React.createElement("div", { className: "row ", style: { backgroundColor: '#f1f1f1' } },
	                        React.createElement("h3", null, "\u00A0"),
	                        React.createElement("div", { className: "col-md-4" },
	                            React.createElement("button", { className: "reg_btn", onClick: function () { _this.saveChildrenInfo(); } }, "\u0417\u0431\u0435\u0440\u0435\u0433\u0442\u0438")),
	                        React.createElement("div", { className: "col-md-6" }, "."),
	                        React.createElement("div", { className: "col-md-12" }, "\u00A0"))
	                    : '');
	        return (page);
	    };
	    return ChildInfo;
	}(React.Component));
	module.exports = ChildInfo;


/***/ },
/* 543 */
/***/ function(module, exports, __webpack_require__) {

	"use strict";
	var __extends = (this && this.__extends) || (function () {
	    var extendStatics = Object.setPrototypeOf ||
	        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
	        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
	    return function (d, b) {
	        extendStatics(d, b);
	        function __() { this.constructor = d; }
	        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
	    };
	})();
	var React = __webpack_require__(1);
	var DatePicker = __webpack_require__(271);
	/**
	 * this.props.date  - input date
	 * this.props.parentFunc(date)  - output date through parent function
	 */
	var DateInput = (function (_super) {
	    __extends(DateInput, _super);
	    function DateInput(props) {
	        var _this = _super.call(this, props) || this;
	        _this.dayLabels = ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
	        _this.monthLabels = ['Сiчень', 'Лютий', 'Березень', 'Квiтень', 'Травень', 'Червень', 'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень'];
	        _this.state = {
	            date_of_ISO: !!_this.props.dateComp ? _this.props.dateComp : ''
	        };
	        return _this;
	    }
	    DateInput.prototype.render = function () {
	        var _this = this;
