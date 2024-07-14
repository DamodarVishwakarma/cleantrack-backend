(function($) {
    "use strict";




	//#chart_widget_4
	if(jQuery('#chart_widget_4').length > 0 ){
    const chart_widget_4 = document.getElementById("chart_widget_4").getContext('2d');

    // chart_widget_4.height = 100;

    let barChartData = {
        defaultFontFamily: 'Poppins',
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{
            label: 'Expense',
            backgroundColor: '#fff',
            hoverBackgroundColor: '#eee',
            data: [
                '20',
                '14',
                '18',
                '25',
                '27',
                '22',
                '12',
                '24',
                '20',
                '14',
                '18',
                '16'
            ]
        }, {
            label: 'Earning',
            backgroundColor: 'rgba(255,255,255,0.1)',
            hoverBackgroundColor: 'rgba(255,255,255,0.15)',
            data: [
                '12',
                '18',
                '14',
                '7',
                '5',
                '10',
                '20',
                '8',
                '12',
                '18',
                '14',
                '16'
            ]
        }]

    };

    new Chart(chart_widget_4, {
        type: 'bar',
        data: barChartData,
        options: {
            legend: {
                display: false
            },
            title: {
                display: false
            },
            tooltips: {
                mode: 'index',
                intersect: false
            },
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                xAxes: [{
                    display: false,
                    stacked: true,
                    barPercentage: 0.2,
                    ticks: {
                        display: false
                    },
                    gridLines: {
                        display: false,
                        drawBorder: false
                    }
                }],
                yAxes: [{
                    display: false,
                    stacked: true,
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        display: false
                    }
                }]
            }
        }
    });
	}




    // var data = {
    //     labels: ["0", "1", "2", "3", "4", "5", "6", "0", "1", "2", "3", "4", "5", "6"],
    //     datasets: [{
    //         label: "My First dataset",
    //         backgroundColor: "rgba(0,131,143,1)",
    //         strokeColor: "rgba(0,131,143,1)",
    //         pointColor: "rgba(0,0,0,0)",
    //         pointStrokeColor: "rgba(0,0,0,0)",
    //         pointHighlightFill: "rgba(0,131,143,1)",
    //         pointHighlightStroke: "rgba(0,131,143,1)",
    //         data:  [35, 18, 15, 35, 40, 20, 30, 25, 22, 20, 45, 35]
    //     }]
    // };



   if(jQuery('#areaChart_2').length > 0 ){
		const areaChart_2 = document.getElementById("areaChart_2").getContext('2d');
		//generate gradient
		const areaChart_2gradientStroke = areaChart_2.createLinearGradient(0, 1, 0, 500);
		areaChart_2gradientStroke.addColorStop(0, "rgba(16, 202, 147, 0.1)");
		areaChart_2gradientStroke.addColorStop(1, "rgba(16, 202, 147, 0)");

		areaChart_2.height = 50;

		new Chart(areaChart_2, {
			type: 'line',
			data: {
				defaultFontFamily: 'Poppins',
				labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
				datasets: [
					{
						label: "My First dataset",
						data: [60, 80, 60, 40, 70, 55, 95],
						borderColor: "#10ca93",
						borderWidth: "3",
						backgroundColor: areaChart_2gradientStroke
					}
				]
			},
			options: {

				tooltips: {
					enabled: false,
				},
				elements: {
						point:{
							radius: 0
						}
				},
				legend: false,
				scales: {
					yAxes: [{

						ticks: {
							beginAtZero: true,
							max: 100,
							min: 0,
							stepSize: 10,
							padding: 2
						},
						display:false,
					}],
					xAxes: [{
						ticks: {
							padding: 2
						},
						display:false,
					}]
				}
			}
		});
	}

let draw = Chart.controllers.line.__super__.draw; //draw shadow

//#chart_widget_2
if(jQuery('#chart_widget_2').length > 0 ){

    const chart_widget_2 = document.getElementById("chart_widget_2").getContext('2d');
    //generate gradient
    const chart_widget_2gradientStroke = chart_widget_2.createLinearGradient(0, 0, 0, 250);
    chart_widget_2gradientStroke.addColorStop(0, "#a0bfff");
    chart_widget_2gradientStroke.addColorStop(1, "#a0bfff");

    // chart_widget_2.attr('height', ['100');

    new Chart(chart_widget_2, {
        type: 'bar',
        data: {
            defaultFontFamily: 'Poppins',
                labels: ["", "", "", "", "", "", "", "", "", "", "", ""],
            datasets: [
                {
                    label: "",
                    data: [65, 59, 80, 81, 56, 55, 40, 88, 45, 95, 54, 76],
                    borderColor: chart_widget_2gradientStroke,
                    borderWidth: "0",
                    backgroundColor: chart_widget_2gradientStroke,
                    hoverBackgroundColor: chart_widget_2gradientStroke
                }
            ]
        },
        options: {
            legend: false,
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                yAxes: [{
                    display: false,
                    ticks: {
                        beginAtZero: true,
                        display: false,
                        max: 100,
                        min: 0,
                        stepSize: 10
                    },
                    gridLines: {
                        display: false,
                        drawBorder: false
                    }
                }],
                xAxes: [{
                    display: false,
                    barPercentage: 0.3,
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        display: false
                    }
                }]
            }
        }
    });

}


//#chart_widget_5
if(jQuery('#chart_widget_5').length > 0 ){
    new Chartist.Line("#chart_widget_5", {
        labels: ["1", "2", "3", "4", "5", "6", "7", "8"],
        series: [
            [4, 5, 3.5, 4, 5, 5.5, 5.8, 4.6]
        ]
    },
	{
        low: 0,
        showArea: 1,
        showPoint: !0,
        showLine: !0,
        fullWidth: !0,
        lineSmooth: !1,
        chartPadding: {
            top: 2,
            right: 0,
            bottom: 0,
            left: 0
        },
        axisX: {
            showLabel: !1,
            showGrid: !1,
            offset: 0
        },
        axisY: {
            showLabel: !1,
            showGrid: !1,
            offset: 0
        }
    });
}

    $(".peity-line").peity("line", {
        fill: ["rgba(32, 222, 166, 1)"],
        stroke: 'rgb(70, 255, 200)',
        width: "400",
        height: "100"
    });


    $(".peity-line2").peity("line", {
        fill: ["rgba(94, 143, 244, 1)"],
        stroke: 'rgb(70, 255, 200)',
        width: "400",
        height: "100"
    });

	 jQuery('.dz-chat-user-box .dz-chat-user').on('click',function(){
		 jQuery('.dz-chat-user-box').addClass('d-none');
		 jQuery('.dz-chat-history-box').removeClass('d-none');
	 });

	jQuery('.dz-chat-history-back').on('click',function(){
		 jQuery('.dz-chat-user-box').removeClass('d-none');
		  jQuery('.dz-chat-history-box').addClass('d-none');
	 });


	var direction =  getUrlParams('dir');
	if(direction != 'rtl')
	{direction = 'ltr'; }

})(jQuery);