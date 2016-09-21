// Generated by CoffeeScript 1.8.0
(function() {
  var beginRandomSequence, clearSelectedProvinces, loadCityList, main, onAreaChange, passedCity, reDrawCities, reloadConstraintCities, setChosenCity, setCities, setRandomCity,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  this.allCities = {};

  this.constraintCities = {};

  this.selectedProvinces = [];

  this.mapName = '我们去哪儿';

  this.interval = null;

  setCities = (function(_this) {
    return function(name, cities) {
      var data, nameMap, option;
      data = [];
      _.map(cities, function(value, city) {
        var v;
        if (__indexOf.call(this.constraintCities, city) >= 0) {
          v = 'in';
        } else {
          v = 'out';
        }
        return data.push({
          name: city,
          value: value.pos.concat(v)
        });
      });
      nameMap = {
        old_city: '历史文化名城',
        unusual_city: '冷门旅游城市',
        china_city: '中国城市'
      };
      _this.mapChart.setOption({
        title: {
          text: nameMap[name]
        }
      });
      option = _this.mapChart.getOption();
      option.series = [
        {
          name: 'cities',
          type: 'scatter',
          coordinateSystem: 'geo',
          symbolSize: 4,
          itemStyle: {
            normal: {
              color: function(o) {
                if (o.data.value[2] === 'in') {
                  return 'green';
                } else {
                  return 'rgb(100, 120, 100)';
                }
              }
            }
          },
          data: data
        }
      ];
      return _this.mapChart.setOption(option, true);
    };
  })(this);

  reDrawCities = (function(_this) {
    return function() {
      var data, series;
      series = _this.mapChart.getOption().series;
      if (series != null ? series.length : void 0) {
        data = [];
        _.map(_this.allCities, function(value, city) {
          var v;
          if (_.has(this.constraintCities, city)) {
            v = 'in';
          } else {
            v = 'out';
          }
          return data.push({
            name: city,
            value: value.pos.concat(v)
          });
        });
        _.filter(series, {
          name: 'cities'
        })[0].data = data;
        return _this.mapChart.setOption({
          series: series
        });
      }
    };
  })(this);

  passedCity = (function(_this) {
    return function(name, val) {
      var data, series;
      data = [
        {
          name: name,
          value: val.pos.concat(2)
        }
      ];
      series = _this.mapChart.getOption().series;
      if (series.length > 1) {
        series = _.filter(series, {
          name: 'cities'
        });
      }
      series.push({
        name: '路过城市',
        type: 'scatter',
        coordinateSystem: 'geo',
        symbolSize: 10,
        label: {
          normal: {
            show: true,
            formatter: '{b}',
            position: 'top'
          }
        },
        itemStyle: {
          normal: {
            color: 'blue'
          }
        },
        data: data
      });
      return _this.mapChart.setOption({
        series: series
      });
    };
  })(this);

  setChosenCity = (function(_this) {
    return function(name, val) {
      var data, series;
      data = [
        {
          name: name,
          value: val.pos.concat('选中')
        }
      ];
      series = _this.mapChart.getOption().series;
      if (series.length > 1) {
        series = _.filter(series, {
          name: 'cities'
        });
      }
      series.push({
        name: '选中城市',
        type: 'scatter',
        coordinateSystem: 'geo',
        symbolSize: 13,
        label: {
          normal: {
            show: true,
            formatter: '{b}',
            position: 'top'
          }
        },
        itemStyle: {
          normal: {
            color: 'blue'
          }
        },
        data: data
      });
      _this.mapChart.setOption({
        series: series,
        title: {
          text: "选定在 " + name
        }
      });
      return $("#go").removeClass('loading');
    };
  })(this);

  clearSelectedProvinces = (function(_this) {
    return function() {
      var province, _i, _len, _ref;
      _ref = _this.selectedProvinces;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        province = _ref[_i];
        _this.mapChart.dispatchAction({
          type: 'geoUnSelect',
          name: province
        });
      }
      _this.mapChart.resize();
      return _this.selectedProvinces = [];
    };
  })(this);

  loadCityList = function(city_name) {
    window.mapChart.showLoading();
    clearSelectedProvinces();
    return fetch("/static/json/" + city_name + ".json").then(function(resp) {
      return resp.json().then(function(cities) {
        window.allCities = cities;
        reloadConstraintCities();
        setCities(city_name, window.allCities);
        $("#go").removeClass('disabled');
        return window.mapChart.hideLoading();
      });
    });
  };

  reloadConstraintCities = (function(_this) {
    return function() {
      _this.constraintCities = {};
      if (_this.selectedProvinces.length) {
        _.map(_this.allCities, function(v, k) {
          var _ref;
          if (_ref = v.pr, __indexOf.call(selectedProvinces, _ref) >= 0) {
            return _this.constraintCities[k] = v;
          }
        });
      } else {
        _this.constraintCities = _.clone(_this.allCities);
      }
      return reDrawCities();
    };
  })(this);

  onAreaChange = (function(_this) {
    return function(params) {
      console.log(params);
      _this.selectedProvinces = [];
      _.map(params.selected, function(v, k) {
        if (v) {
          return _this.selectedProvinces.push(k);
        }
      });
      return reloadConstraintCities();
    };
  })(this);

  setRandomCity = (function(_this) {
    return function() {
      var name, names;
      names = _.keys(_this.constraintCities);
      name = names[_.random(0, names.length - 1)];
      return passedCity(name, _this.allCities[name]);
    };
  })(this);

  beginRandomSequence = (function(_this) {
    return function() {
      var addedTime, city, randomSequence, timeGap, _i, _len, _ref;
      randomSequence = _.sampleSize(_.keys(_this.constraintCities), 5);
      timeGap = 1000;
      addedTime = 0;
      $("#go").addClass("loading");
      _ref = randomSequence.slice(0, -1);
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        city = _ref[_i];
        addedTime += timeGap;
        timeGap -= 100;
        setTimeout(_.partial(passedCity, city, _this.constraintCities[city]), addedTime);
      }
      addedTime += timeGap;
      city = _.last(randomSequence);
      return setTimeout(_.partial(setChosenCity, city, _this.constraintCities[city]), addedTime);
    };
  })(this);

  main = (function(_this) {
    return function() {
      _this.mapChart = echarts.init($("#chart")[0]);
      mapChart.setOption({
        title: {
          text: '我们去哪儿玩',
          top: '15',
          left: 'center',
          textStyle: {
            color: '#555'
          }
        },
        backgroundColor: '#bbbbbb',
        tooltip: {
          show: true,
          showContent: true,
          trigger: 'item',
          position: 'top',
          formatter: '{b}',
          backgroundColor: 'black',
          textStyle: {
            color: '#1a2'
          }
        },
        geo: {
          map: 'china',
          label: {
            emphasis: {
              show: false
            }
          },
          itemStyle: {
            normal: {
              color: '#751',
              areaColor: '#cca',
              borderColor: '#000'
            }
          },
          selectedMode: 'multiple'
        },
        series: []
      });
      _this.mapChart.on('geoselectchanged', onAreaChange);
      $('#china-city').click(_.partial(loadCityList, 'china_city'));
      $('#old-city').click(_.partial(loadCityList, 'old_city'));
      $('#unusual').click(_.partial(loadCityList, 'unusual_city'));
      return $("#go").click(beginRandomSequence);
    };
  })(this);

  $(main);

}).call(this);
