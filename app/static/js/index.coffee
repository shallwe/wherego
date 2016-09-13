setRandomCity = =>
    names = _.keys @cities
    city = names[_.random 0, names.length-1]
    data = [{
        name: city
        value: @cities[city].concat(city)
    }]

    @mapChart.setOption
        series:
            data: data

toggleRandom = =>
    if @interval
        clearInterval @interval
        @interval = null
    else
        @interval = setInterval setRandomCity, 500



main = =>
    @mapChart = echarts.init $("#chart")[0]
    mapChart.setOption
        title:
            text: '我们去哪玩儿(点击地图开始选择)'
            textStyle:
                color: '#fff'
        backgroundColor: '#404a59'

        tooltip:
            show: true
            showContent: true
            trigger: 'item'
            position: 'top'
            formatter: '{a} {b} {c}'
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
                        areaColor: '#0f0'
                        borderColor: '#111'

        series: [
            name: '踪迹'
            type: 'scatter'
            coordinateSystem: 'geo'
            symbolSize: 10
            label:
                normal:
                    show: true
                    formatter: '{b}'
                    textStyle:
                        color: 'black'
                    position: 'top'
                emphasis:
                    show: false

            itemStyle:
                emphasis:
                    borderColor: '#fff'
                    borderWidth: 1
            data: []
        ]


    $.getJSON("/static/china.json", (resp) =>
        @provinces = resp
        @cities = {}
        _.map provinces, (p, cs) =>
            _.merge @cities, p

        @mapChart.on 'click', toggleRandom


    )
$ main