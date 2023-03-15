odoo.define('vehicle_rental.online_rent_request', function(require)
{
var publicWidget = require('web.public.widget');
var rpc = require('web.rpc');

publicWidget.registry.PublicWidgetOnlineRentRequest = publicWidget.Widget.extend({
     selector: '.online_req',
     events: {
        'change #vehicle_form': '_onVehicleChange',
        'change #from_date': '_onFromDateChange',
        'change #charge_id': '_onChargeIdChange',
    },
      _onVehicleChange: function (ev) {
            var vehicle_id = ev.target.value
            rpc.query({
            model:'rent.charge',
            method:'check_period',
            args:[,vehicle_id],
        })
         .then(function (data) {
                 $('#charge_id').empty();
                 data.forEach(function(result){
                   var charge = Object.values(result)
                   var charge_id = Object.keys(result)
                   $('#charge_id').append($('<option></option>').attr('value',charge_id).text(charge))
                 })
                            })
    },
      _onFromDateChange: function (ev) {
            var from_date = ev.target.value
            var charge_id = this.$('#charge_id').val()
            rpc.query({
            model:'rent.request',
            method:'check_to_date',
            args:[,from_date,charge_id],
        })
        .then(function (data) {
                 $('#to_dateq').val(data)
                 })
    },
      _onChargeIdChange : function (ev) {
               var charge_id = ev.target.value
               var from_date = $('#from_date1').val()
                rpc.query({
                    model:'rent.request',
                    method:'check_amount',
                    args:[,charge_id],
                })
                .then(function (data) {
                     $('#amount1').val(data)
                 })
                rpc.query({
                    model:'rent.request',
                    method:'check_to_date',
                    args:[,from_date,charge_id],
                })
                .then(function (data) {
                    $('#to_dateq').val(data)
               })
      },
});
});