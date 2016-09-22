@allCities = {} #{name: {pos: [111,112], pr: province}}
@constraintCities = {}
@selectedProvinces = []
@mapName = '我们去哪儿'
@interval = null



setCities = (name, cities) =>
    data = []
    _.map cities, (value, city) ->
        if city in @constraintCities
            v = 'in'
        else
            v = 'out'
        data.push
            name: city
            value: value.pos.concat v
    nameMap =
        old_city: '历史文化名城'
        unusual_city: '冷门旅游城市'
        china_city: '中国城市'

    @mapChart.setOption
        title:
            text: nameMap[name]
    option = @mapChart.getOption()
    option.series = [{
            name: 'cities'
            type: 'scatter'
            coordinateSystem: 'geo'
            symbolSize: 4
            itemStyle:
                normal:
                    color: (o) ->
                        if o.data.value[2] == 'in' then 'green' else 'rgb(100, 120, 100)'
            data: data
        }]

    @mapChart.setOption(option, true)

reDrawCities = =>
    series = @mapChart.getOption().series
    if series?.length
        data = []
        _.map @allCities, (value, city) ->
            if _.has @constraintCities, city
                v = 'in'
            else
                v = 'out'
            data.push
                name: city
                value: value.pos.concat v
        _.filter(series, name: 'cities')[0].data = data
        @mapChart.setOption series: series


passedCity = (name, val) =>
    data = [{
        name: name
        value: val.pos.concat 2
    }]
    series = @mapChart.getOption().series

    if series.length > 1
        series = _.filter series, name: 'cities'
    series.push
        name: '路过城市'
        type: 'scatter'
        coordinateSystem: 'geo'
        symbolSize: 10
        label:
            normal:
                show: true
                formatter: '{b}'
                position: 'top'
        itemStyle:
            normal:
                color: 'blue'
        data: data

    @mapChart.setOption
        series: series


setChosenCity = (name, val) =>
    data = [{
        name: name
        value: val.pos.concat '选中'
    }]
    series = @mapChart.getOption().series

    if series.length > 1
        series = _.filter series, name: 'cities'
    series.push
        name: '选中城市'
        type: 'scatter'
        coordinateSystem: 'geo'
        symbolSize: 13
        label:
            normal:
                show: true
                formatter: '{b}'
                position: 'top'
        itemStyle:
            normal:
                color: 'green'
        data: data

    @mapChart.setOption
        series: series
        title:
            text: "所以,我们去 『#{name}』 ?"
    $("#go").removeClass('loading')

clearSelectedProvinces = =>
    for province in @selectedProvinces
        @mapChart.dispatchAction
            type: 'geoUnSelect'
            name: province
    @mapChart.resize()
    @selectedProvinces = []



loadCityList = (city_name) ->
    window.mapChart.showLoading()
    clearSelectedProvinces()
    $.getJSON "/static/json/#{city_name}.json", (cities) ->
        window.allCities = cities
        reloadConstraintCities()

        setCities city_name, window.allCities
        $("#go").removeClass('disabled')
        window.mapChart.hideLoading()
    $('.city-selector .button').removeClass('active')
    $("##{city_name}").addClass('active')

reloadConstraintCities = =>
    @constraintCities = {}
    if @selectedProvinces.length
        _.map @allCities, (v, k) =>
            if v.pr in selectedProvinces
                @constraintCities[k] = v
    else
        @constraintCities = _.clone @allCities
    reDrawCities()

onAreaChange = (params) =>
    console.log params
    @selectedProvinces = []
    _.map params.selected, (v, k) =>
        if v
            @selectedProvinces.push k

    reloadConstraintCities()

setRandomCity = =>
    names = _.keys @constraintCities
    name = names[_.random 0, names.length - 1]
    passedCity(name, @allCities[name])

beginRandomSequence = =>
    randomSequence = _.sampleSize _.keys(@constraintCities), 5
    timeGap = 1000
    addedTime = 0

    $("#go").addClass("loading")
    @mapChart.setOption(
        title:
            text:
                '小公鸡点到谁。。'
    )

    for city in randomSequence[0...-1]
        addedTime += timeGap
        timeGap -= 100
        setTimeout _.partial(
            passedCity, city, @constraintCities[city]
        ), addedTime

    addedTime += timeGap
    city = _.last randomSequence
    setTimeout _.partial(
        setChosenCity, city, @constraintCities[city]
    ), addedTime


main = =>
    @mapChart = echarts.init $("#chart")[0]
    mapChart.setOption
        title:
            text: '我们去哪儿玩'
            top: '15'
            left: 'center'
            textStyle:
                color: '#555'
        backgroundColor: '#bbbbbb'

        tooltip:
            show: true
            showContent: true
            trigger: 'item'
            position: 'top'
            formatter: '{b}'
            backgroundColor: 'black'
            textStyle:
                color: '#1a2'

        geo:
            map: 'china'
            label:
                emphasis:
                    show: false

            itemStyle:
                normal:
                    color: '#751'
                    areaColor: '#cca'
                    borderColor: '#000'
            selectedMode: 'multiple'

        series: []


    @mapChart.on 'geoselectchanged', onAreaChange

    $('#china_city').click _.partial(loadCityList, 'china_city')
    $('#old_city').click _.partial(loadCityList, 'old_city')
    $('#unusual_city').click _.partial(loadCityList, 'unusual_city')
    $('#airport_city').click _.partial(loadCityList, 'airport_city')

    $("#go").click beginRandomSequence
$ main