	// ListRequestsOnKindergarten
	// this.props.numberDc - number of kindergarten  
	var upFilter = ['', '', '', '', ''];
	var ListRequestsOnKindergarten = React.createClass({
	    responceError: '', l_showComponent: [], arrowFilter: [], upFilter: [], listRequests: [], group: [], userOrders: [],
	    getInitialState: function () {
	        return {
	            numShowComponent: 0,
	            listRequests: [],
	            buttomMore: false
	        };
	    },
	    componentWillMount: function () {
	        var _this = this;
	        var list_of_children = [];
	        this.listRequests = [];
	        this.group = [];
	        this.upFilter = [];
	        !!auth.authObj.user
	            && !!auth.authObj.user.email
	            ? this.userOrder().then(function (listReq) {
	                _this.userOrders = listReq;
	                _this.initDataComponent();
	            }).catch(function (x) {
	                _this.responceError = x;
	                _this.setState({ numShowComponent: 2 });
	            })
	            : this.initDataComponent();
	        this.l_showComponent[1] = function () {
	            //*
	            // show children in group
	            // function
	            var age_group = function (param_item, i) {
	                var arrowFilter = [];
	                // this.upFilter[i].forEach((item, i1) => arrowFilter[i1] = item === 'up' ? 'down-filter' : 'up-filter');
	                // check queue number 
	                var queueNumber = [];
	                var new_listStrok = param_item.sort(function (a, b) { return +a.queueNumber.slice(0, -4) - +b.queueNumber.slice(0, -4); });
	                new_listStrok.forEach(function (item1, k) {
	                    _this.userOrders.forEach(function (item2, k2) {
	                        if (item2.statuses[item2.statuses.length - 1].name !== 'removed'
	                            && item2.child.birthCertificate.number.localeCompare(item1.child.birthCertificate.number) === 0) {
	                            queueNumber.push({ request: item1, queueNumber: k });
	                        }
	                    });
	                });
	                var queuejsxStr = !!queueNumber
	                    ? queueNumber.map(function (item) {
	                        return (React.createElement("p", { style: { fontWeight: '700', fontSize: '13px' } },
	                            "Заявка на свідоцтво ",
	                            item.request.child.birthCertificate.number,
	                            " в цьому списку, перед нею ",
	                            item.queueNumber,
	                            " інших."));
	                    })
	                    : '';
	                // i - number strok of group, el - # column of table 
	                // function 
	                var clickUpDownTitle = function (i, el) {
	                    _this.upFilter[i][el] = _this.upFilter[i][el] === 'up' ? 'down' : 'up';
	                    _this.setState({ numShowComponent: 1 });
	                };
	                list_of_children[i] = React.createElement(ListOfOrdersByAge, { key: param_item[0]._id, name: param_item[0]._id, upFilter: upFilter, responceData: new_listStrok, numberDc: _this.props.numberDc });
	                /*  <div className="col-md-3 filtr" onClick={(e) => clickUpDownTitle(i, 0)}>
	                                              ім'я дитини<div className={arrowFilter[0]}></div></div>
	              */
	                return (React.createElement("div", null,
	                    React.createElement("br", null),
	                    React.createElement("p", null,
	                        "Вікова група вiд ",
	                        param_item[0].ageLimitFrom,
	                        " до ",
	                        param_item[0].ageLimitTo,
	                        " рокiв"),
	                    queuejsxStr,
	                    React.createElement("div", { className: "row row-order-list-title" },
	                        React.createElement("div", { className: "col-md-2 col-sm-2 col-xs-12  filtr" }, "ім'я дитини"),
	                        React.createElement("div", { className: "col-md-2 col-sm-2 col-xs-12  filtr" }, "серія та номер свідоцтва"),
	                        React.createElement("div", { className: "col-md-1 col-sm-1 col-xs-12  filtr" }, "дата заявки"),
	                        React.createElement("div", { className: "col-md-2 col-sm-2 col-xs-12  filtr" }, "бажана дата вступу"),
	                        React.createElement("div", { className: "col-md-2 col-sm-2 col-xs-12  filtr" }, "статус заявки"),
	                        React.createElement("div", { className: "col-md-2 col-sm-2 col-xs-12  filtr" }, "додатково")),
	                    list_of_children[i]));
	            };
	            // sort by ageLimitFrom
	            // function
	            var sortByageLimitFrom = function (in_orders) {
	                var Orders = in_orders.slice();
	                // bubble sort
	                var num_sort, tempVal, sort_mass = true;
	                num_sort = 'ageLimitFrom';
	                if (num_sort !== undefined) {
	                    while (sort_mass) {
	                        sort_mass = false;
	                        for (var i = 0; i < Orders.length; i++) {
	                            if (i + 1 < Orders.length) {
	                                if (Orders[i][num_sort] > Orders[i + 1][num_sort]) {
	                                    sort_mass = true;
	                                    tempVal = Orders[i + 1];
	                                    Orders[i + 1] = Orders[i];
	                                    Orders[i] = tempVal;
	                                }
	                            }
	                        }
	                    }
	                }
	                return (Orders);
	            };
	            // function
	            var splitByageLimitFrom = function (in_orders) {
	                var ByageLimitFrom = [], return_ByageLimitFrom = [], remeber_value;
	                remeber_value = in_orders[0].ageLimitFrom;
	                ByageLimitFrom[remeber_value] = [];
	                for (var i = 0; i < in_orders.length; i++) {
	                    if (in_orders[i].ageLimitFrom !== remeber_value) {
	                        remeber_value = in_orders[i].ageLimitFrom;
	                        ByageLimitFrom[remeber_value] = [];
	                        ByageLimitFrom[remeber_value].push(in_orders[i]);
	                    }
	                    else {
	                        ByageLimitFrom[remeber_value].push(in_orders[i]);
	                    }
	                }
	                return_ByageLimitFrom = ByageLimitFrom.filter(function (item) { return item !== undefined; });
	                // return [][]
	                return (return_ByageLimitFrom);
	            };
	            var mOut = _this.group.map(function (item, i) {
	                if (typeof item === 'object')
	                    return (React.createElement("div", null,
	                        React.createElement("br", null),
	                        React.createElement("h4", null,
	                            "Навчальний рiк ",
	                            item[0].periodFrom,
	                            " / ",
	                            item[0].periodTo),
	                        splitByageLimitFrom(sortByageLimitFrom(item))
	                            .map(function (item1) {
	                            return age_group(item1, i);
	                        })));
	                else
	                    return ('');
	            });
	            //return mOut;
	            var out = mOut.map(function (item) { return React.createElement("div", null, item); });
	            return React.createElement("div", null, out);
	        };
	        this.l_showComponent[0] = function () {
	            return (React.createElement("div", { className: "col-md-12" },
	                React.createElement("img", { src: "img/loading.gif", width: "100px" })));
	        };
	        // error from server
	        this.l_showComponent[2] = function (errorMessage) {
	            return (React.createElement("div", { className: "error-block" },
	                "Произошла ошибка при загрузке страницы. ",
	                errorMessage));
	        };
	        // nothing
	        this.l_showComponent[3] = function () {
	            return (React.createElement("div", null));
	        };
	    },
	    initDataComponent: function (last_id) {
	        var _this = this;
	        if (last_id === void 0) { last_id = undefined; }
	        // show more request after click button "завантажити більше "   + '&last_status=approved,need-additional-check,invite-sent,invite-accepted'
	        var linkPost = 'requests/main_info?with_selected_kindergarten='
	            + this.props.numberDc
	            + (!!last_id ? '&request_to=' + last_id : '');
	        httpRequest.ajaxCall_GET(linkPost, true)
	            .then(function (xStr) {
	            var xObj = JSON.parse(xStr);
	            if (xObj.data !== undefined) {
	                // set state init data 
	                if (xObj.data.length >= config.strokOnPage) {
	                    _this.listRequests = _this.listRequests.concat(xObj.data);
	                    _this.initDataComponent(xObj.data[xObj.data.length - 1]._id);
	                }
	                else {
	                    _this.listRequests = _this.listRequests.concat(xObj.data);
	                    _this.listRequests = _this.listRequests.filter(function (item) {
	                        return !item.statuses[item.statuses.length - 1].name.localeCompare('approved')
	                            || !item.statuses[item.statuses.length - 1].name.localeCompare('need-additional-check')
	                            || !item.statuses[item.statuses.length - 1].name.localeCompare('invite-sent')
	                            || !item.statuses[item.statuses.length - 1].name.localeCompare('invite-accepted')
	                            || !item.statuses[item.statuses.length - 1].name.localeCompare('invite-declined');
	                    });
	                    _this.initGroup(); // 
	                    _this.setState({ numShowComponent: 1 });
	                }
	            }
	            else {
	                if (xObj.error !== undefined) {
	                    _this.responceError = xObj.error.message;
	                    _this.setState({ numShowComponent: 2 });
	                }
	            }
	        })
	            .catch(function (x) {
	            console.log('Error. Get loading MORE list requests on kindergarten. Responce from server, ' + x);
	            if (typeof (x) === "object") {
	                _this.responceError = 'Error. Get loading more list requests on kindergarten. Responce from server , ' + x;
	                _this.setState({ numShowComponent: 2 });
	            }
	        });
	    },
	    // get requests for registration user
	    // return list of requests
	    userOrder: function () {
	        var _this = this;
	        return new Promise(function (resolve, reject) {
	            var linkPost = 'requests?email=' + auth.authObj.user.email;
	            httpRequest.ajaxCall_GET(linkPost, true)
	                .then(function (xStr) {
	                var xObj = JSON.parse(xStr);
	                if (xObj.data !== undefined) {
	                    resolve(xObj.data);
	                }
	                else {
	                    if (xObj.error !== undefined) {
	                        _this.responceError = xObj.error.message;
	                        reject(_this.responceError);
	                    }
	                }
	            })
	                .catch(function (x) {
	                console.log('Error. Get loading user orders error, ' + x);
	                reject('Error. Get loading user orders error, ' + x);
	            });
	        });
	    },
	    initGroup: function () {
	        var _this = this;
	        // array groups by age. [<>,<>,[{2 year}],[{3 year}],...]
	        this.listRequests.forEach(function (item, i) {
	            var periodFrom = item.periodFrom;
	            typeof _this.group[periodFrom] === "undefined"
	                ? (_this.group[periodFrom] = []) : null;
	            _this.group[periodFrom].push(item);
	        });
	        this.group = this.group.filter(function (item) { return item !== undefined; });
	    },
	    render: function () {
	        var showCode = this.l_showComponent[this.state.numShowComponent](this.responceError);
	        return (React.createElement("div", null, showCode));
	    }
	});
