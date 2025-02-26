// ==UserScript==
// @name         Peculiar Inventory Scraper
// @namespace    https://cagivens.github.io/
// @version      2025-02-22
// @description  Searches currently viewed peculiar inventory bucket for records, then downloads them as .csv
// @author       caleigiv
// @downloadURL  https://cagivens.github.io/userscripts/Peculiar%Inventory%Scraper-2025-02-22.user.js
// @updateURL    https://cagivens.github.io/userscripts/Peculiar%Inventory%Scraper-2025-02-22.user.js
// @match        http://peculiar-inventory-na.aka.corp.amazon.com/MDT1/report/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=amazon.com
// @require      https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    $(document).ready(function(){
        function createButton() {
            const buttonContainer = document.createElement('span');
            const button = document.createElement('button');
            buttonContainer.classList.add('a-button-inner');
            buttonContainer.appendChild(button);
            button.classList.add('listifyButton');
            button.innerHTML = 'Export to CSV';
            return buttonContainer;
        }
        $('div.a-column.a-span12')[1].append(createButton());
        $('.listifyButton').click(function(){
            function saveCSV(data) {
                var bucket = window.location.href.split('/');
                bucket = bucket[bucket.length - 1];
                bucket = bucket.substring(0, bucket.indexOf('?'))
                var date = new Date();
                var filename = `peculiar_inventory_data_${bucket}_${date.getYear()}${date.getMonth()}${date.getDay()}.csv`;
                var file = new Blob([data], {type: 'text/plain'});
                var downloadElement = document.createElement('a');
                downloadElement.setAttribute('href', window.URL.createObjectURL(file));
                downloadElement.setAttribute('download', filename);
                document.body.appendChild(downloadElement);
                downloadElement.click();
            }
            function sweepContainer(containerArray) {
                var resultString = '';
                for(var i = 0; i < containerArray.length; i++) {
                    containerArray[i].getElementsByTagName('button')[0].click();
                    const currentContainer = containerArray[i].getElementsByClassName('textCol')[1].firstChild == null ? '' : containerArray[i].getElementsByClassName('textCol')[1].firstChild.innerHTML;
                    const containerType = containerArray[i].getElementsByClassName('textCol')[2].innerHTML;
                    const parent = containerArray[i].getElementsByClassName('textCol')[3].firstChild == null ? '' : containerArray[i].getElementsByClassName('textCol')[3].firstChild.innerHTML;
                    const parentType = containerArray[i].getElementsByClassName('textCol')[4].innerHTML;
                    const grandparent = containerArray[i].getElementsByClassName('textCol')[5].firstChild == null ? '' : containerArray[i].getElementsByClassName('textCol')[5].firstChild.innerHTML;
                    const grandparentType = containerArray[i].getElementsByClassName('textCol')[6].innerHTML;
                    const totalRecords = Number(document.getElementById('container-inventory-details_info').innerHTML.split(' ')[5]);
                    var scrapedRecords = 0;
                    var items = document.getElementById('side-panel').getElementsByTagName('tbody')[0].getElementsByTagName('tr');
                    var nextButton = document.getElementById('container-inventory-details_next');
                    for(var j = 0; j < items.length; j++) {
                        const data = items[j].getElementsByTagName('td')
                        resultString += currentContainer + ',';
                        resultString += containerType + ',';
                        resultString += parent + ',';
                        resultString += parentType + ',';
                        resultString += grandparent + ',';
                        resultString += grandparentType + ',';
                        resultString += data[0].innerHTML + ',';
                        resultString += data[1].getElementsByTagName('a')[0].innerHTML + ',';
                        resultString += data[2].innerHTML + ',';
                        resultString += data[3].innerHTML + ',';
                        resultString += data[4].innerHTML + ',\n';
                        scrapedRecords += 1;
                        if(j == items.length - 1) {
                            if(scrapedRecords < totalRecords - 1) {
                                nextButton.click();
                                j = 0;
                                items = document.getElementById('side-panel').getElementsByTagName('tbody')[0].getElementsByTagName('tr');
                            }
                        }
                    }
                }
                return resultString;
            }
            var bucketData = 'Container,Container Type,Parent,Parent Type,Grandparent,Grandparent Type,Estimated Age,FcSku,Quantity,Owner,Disposition,\n';
            bucketData += sweepContainer($('tbody').toArray()[1].getElementsByTagName('tr'));
            saveCSV(bucketData);
        });
    });
})();
