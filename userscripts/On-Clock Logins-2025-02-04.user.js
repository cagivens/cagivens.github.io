// ==UserScript==
// @name         On-Clock Logins
// @namespace    http://tampermonkey.net/
// @version      2025-02-04
// @author       @caleigiv
// @description  Downloads logins of associates that are on the clock as CSV.
// @author       You
// @match        https://fclm-portal.amazon.com/reports/timeOnTask*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=amazon.com
// @grant        none
// @require      https://code.jquery.com/jquery-3.6.0.min.js
// ==/UserScript==

(function() {
    'use strict';

    // Creating button to represent script
    $('.cp-submit-row').prepend('<a id="on-clock-logins-button" class="cp-submit">Logins</a>');
    // Adding onClick listener to 'Logins' button
    $('#on-clock-logins-button').click(function(){
        // Selecting all rows that contain associate logins
        const rows = $('.tot-row').toArray();
        // Preparing data variable
        var csv = '';
        // Storing all logins in CSV format
        rows.forEach(function(row){
            csv += row.getElementsByTagName('td')[3].innerHTML;
            csv += ',\n'
        });
        // Creating CSV file
        var fileName = 'on-clock-outout.csv';
        var file = new Blob([csv], {type: 'text/plain'});
        // Creating temporary anchor to download file
        var downloadElement = document.createElement('a');
        downloadElement.setAttribute('href', window.URL.createObjectURL(file));
        downloadElement.setAttribute('download', fileName);
        document.body.appendChild(downloadElement);
        // Downloading Associate login CSV
        downloadElement.click();
        // Removing temporary anchor
        document.removeChild(downloadElement);
    });
})();