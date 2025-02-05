// ==UserScript==
// @name         Low Rate Highlighter
// @namespace    http://tampermonkey.net/
// @version      2025-02-04
// @description  Highlights associates with low rates in PPA
// @author       @caleigiv
// @match        https://fclm-portal.amazon.com/ppa/inspect/process?*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=amazon.com
// @grant        none
// @require      https://code.jquery.com/jquery-3.6.0.min.js
// ==/UserScript==

(function() {
    'use strict';
    // Defining GM_addStyle
    function GM_addStyle(css) {
        // Creating or Getting style element
        const style = document.getElementById("GM_addStyleBy8626") || (function() {
            const style = document.createElement('style');
            style.type = 'text/css';
            style.id = "GM_addStyleBy8626";
            document.head.appendChild(style);
            return style;
        })();
        // Inserting new css rule
        const sheet = style.sheet;
        sheet.insertRule(css, (sheet.rules || sheet.cssRules || []).length);
    }
    $(document).ready(function(){
        // Setting target rate
        const targetRate = 26;
        // Getting rows that contain UPH
        const rows = $('#secondaryProductivityList tr').toArray();
        const headerElements = $('#secondaryProductivityList th').toArray();
        var uphIndex = 0;
        // Finding the correct column index to highlight
        for(var h = 0; h < $('#secondaryProductivityList th').toArray().length; h++) {
            try {
                const label = headerElements[h].getElementsByTagName('div')[0].innerHTML;
                if(label.includes("UPH")) {
                    uphIndex = h - 2;
                    break;
                }
            } catch(e) {
                console.error(e.name + ' has occurred\n' + e.message);
            }
        }
        // Giving each row a new class for later animation
        for(var i = 2; i < rows.length; i++) {
            try {
                const fieldContainers = rows[i].getElementsByTagName('td');
                const rateContainer = fieldContainers[uphIndex];
                const currentRate = Number(rateContainer.innerHTML);
            if(currentRate < targetRate) {
                rateContainer.classList.add('lowRate');
            }
            } catch(e) {
                console.error(e.name + ' has occurred on iteration ' + (i - 1) + '\n' + e.message);
            }
        }
        // Creating new css animation
        GM_addStyle('@keyframes highlight {0% {background-color: white; color: black} 50% {background-color: #de645b; color: white;} 100% {background-color: white; color: black;}}');
        // Adding new animation to appropriate cells
        GM_addStyle('.lowRate {background-color: white; color: black; animation-name: highlight; animation-duration: 2s; animation-iteration-count: infinite;}');
    });
})();
