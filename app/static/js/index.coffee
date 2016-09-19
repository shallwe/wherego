@toChoseCity = {}

setRandomCity = =>
    names = _.keys @toChoseCity
    name = names[_.random 0, names.length-1]
    setCity(name, @toChoseCity[name])

setCities = (name, cities) =>
    data = []
    _.map cities, (value, city) ->
        data.push
            name: city
            value: value.concat city
    nameMap =
        old_city: '历史文化名城'
        unusual_city: '冷门旅游城市'
    @mapChart.setOption
        title:
            text: nameMap[name]
        series:
            type: 'scatter'
            coordinateSystem: 'geo'
            label:
                normal:
                    show: false
                    formatter: '{b}'
                    position: 'top'
                emphasis:
                    show: false
            symbolSize: 4
            label:
                normal:
                    show: false
            itemStyle:
                normal:
                    color: 'green'
            data: data

setCity = (name, pos) =>
    data = [{
        name: name
        value: pos.concat name
    }]
    series = @mapChart.getOption().series

    if series.length > 1
        series = _.reject series, name: '选中城市'
    series.push
        name: '选中城市'
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


toggleRandomCity = =>
    if @interval
        clearInterval @interval

        @interval = null
        $("#go .icon").removeClass 'stop'
        $("#go .icon").addClass 'play'
    else
        @interval = setInterval setRandomCity, 1000
        $("#go .icon").removeClass 'start'
        $("#go .icon").addClass 'stop'

loadCity = (city_name)->
    fetch("/static/json/#{city_name}.json").then (resp) ->
        resp.json().then (cities) ->
            window.toChoseCity = cities
            setCities city_name, window.toChoseCity
            $("#go").removeClass('disabled')


main = =>
    @mapChart = echarts.init $("#chart")[0]
    mapChart.setOption
        title:
            text: '我们去哪儿玩'
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
#                    color: '#751'
                    areaColor: '#cca'
                    borderColor: '#000'
            selectedMode: 'multiple'

        series: []




    @mapChart.on 'geoselectchanged', (params) ->
        console.log params

    $('#china-city').click _.partial(loadCity, 'china_city')
    $('#old-city').click _.partial(loadCity, 'old_city')
    $('#unusual').click _.partial(loadCity, 'unusual_city')

    $("#go").click toggleRandomCity
$ main