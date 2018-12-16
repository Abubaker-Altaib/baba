openerp.report_no_download = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;


    instance.web.ActionManager.include({
        ir_actions_report_xml: function (action, options) {
            var cr_options = options
            var self = this;
            instance.web.blockUI();
            return instance.web.pyeval.eval_domains_and_contexts({
                contexts: [action.context],
                domains: []
            }).then(function (res) {
                action = _.clone(action);
                action.context = res.context;
                // iOS devices doesn't allow iframe use the way we do it,
                // opening a new window seems the best way to workaround
                if (navigator.userAgent.match(/(iPod|iPhone|iPad)/)) {
                    var params = {
                        action: JSON.stringify(action),
                        token: new Date().getTime()
                    }
                    var url = self.session.url('/web/report', params)
                    instance.web.unblockUI();
                    $('<a href="' + url + '" target="_blank"></a>')[0].click();
                    return;
                }
                var isFirefox = typeof InstallTrigger !== 'undefined';
                var supportsPdfMimeType = typeof navigator.mimeTypes["application/pdf"] !== "undefined"
                var isIE = function () {
                    return !!(window.ActiveXObject || "ActiveXObject" in window)
                }
                var supportsPdfActiveX = function () {
                    return !!(createAXO("AcroPDF.PDF") || createAXO("PDF.PdfCtrl"))
                }
                var supportsPDFs = supportsPdfMimeType || isIE() && supportsPdfActiveX();

                if ( (action['report_type'] == 'pdf' || !(action['context']['xls_report'] == 1) ) && supportsPDFs &&  ! isFirefox) {
                    var params = {
                        action: JSON.stringify(action),
                        token: new Date().getTime(),
                    }

                    var url = self.session.url('/web/report', params)

                    var popup = window.open("/report_no_download/export/", "_blank", "toolbar=yes,scrollbars=yes,resizable=yes,top=500,left=500,width=800,height=800");




                    popup.document.write('<style> .pdfobject-container { height: 500px;} .pdfobject { border: 1px solid #666; } </style>')

                    popup.document.write('<a href="' + url + '">Download</a>')
                    popup.document.write('<div id="DocViewer"><h1>loading</h1></div>')


                    var options = {
                        pdfOpenParams: {
                            view: "FitV",
                            pagemode: "thumbs",
                            search: "lorem ipsum"
                        }
                    }
                    console.log(self.session.url('/report_no_download/export/') + "&name=" + url)
                    PDFObject.embed(self.session.url('/report_no_download/export/') + "&name=" + url, popup.document.getElementById("DocViewer"), options);

                    instance.web.unblockUI();
                    return;

                }

                

                // if ((action['report_type'] == 'pdf' || !(action['context']['xls_report'] == 1) ) && isFirefox) {
                //     alert('لا يكمنك طباعة  التقرير بمتصفح فيرفكس الرجاء طباعة التقرير بمتصفح اخر')
                //     alert('You can not print the report with firefox browser, please consider using google chrome ')
                //     instance.web.unblockUI();
                //     return
                // }


                if ((action['report_type'] == 'pdf' || !(action['context']['xls_report'] == 1) ) && isFirefox & false) {
                    instance.web.unblockUI();
                    var params = {
                        action: JSON.stringify(action),
                        token: new Date().getTime(),
                    }

                    var url = self.session.url('/web/report', params)


                    var popup = window.open("", "_blank", "toolbar=yes,scrollbars=yes,resizable=yes,top=500,left=500,width=800,height=800");

                    popup.document.body.dir = "rtl"


                    // popup.document.write('<script src="/report_no_download/pdf.js"></script>')
                    popup.document.write('<style> .pdfobject-container { height: 500px;} .pdfobject { border: 1px solid #666; } </style>')

                    popup.document.write('<a href="' + url + '">Download</a>')


                    // popup.document.write('<div>')
                    // popup.document.write('<button id="prev">Previous</button>')
                    // popup.document.write('<button id="next">Next</button>')
                    // popup.document.write('&nbsp; &nbsp;')
                    // popup.document.write('<span>Page: <span id="page_num"></span> / <span id="page_count"></span></span>')
                    // popup.document.write('</div>')

                    // popup.document.write('<canvas width="100%" height="100%" style="border:1px solid #000000;" id="the-canvas"></canvas>')
                    popup.document.write('<div id="container"></div>')

                    popup.document.write('<link type="text/css" href="/report_no_download/static/src/css/text_layer_builder.css" rel="stylesheet">')

                    popup.document.write('<script type="text/javascript" src="/report_no_download/static/src/js/text_layer_builder.js"></script>')


                    url = self.session.url('/report_no_download/export/') + "&name=" + url;



                    // The workerSrc property shall be specified.
                    //PDFJS.workerSrc = self.session.url('/report_no_download/pdf.worker.js');
                    // PDFJS.worker = $.getScript(self.session.url('/report_no_download/pdf.worker.js'));

                    //PDFJS.disableWorker = true;
                    // var pdfDoc = null,
                    //     pageNum = 1,
                    //     pageRendering = false,
                    //     pageNumPending = null,
                    //     scale = 0.8,
                    //     canvas = popup.document.getElementById('the-canvas'),
                    //     ctx = canvas.getContext('2d');
                    // ctx.font = "30px Arial"

                    /**
                     * Get page info from document, resize canvas accordingly, and render page.
                     * @param num Page number.
                     */


                    function renderPagedoc(pdf) {

                        // Get div#container and cache it for later use
                        var container = popup.document.getElementById("container");

                        // Loop from 1 to total_number_of_pages in PDF document
                        for (var i = 1; i <= pdf.numPages; i++) {

                            // Get desired page
                            pdf.getPage(i).then(function (page) {
                                var scale = 1.5;
                                var viewport = page.getViewport(scale);
                                var div = popup.document.createElement("div");

                                // Set id attribute with page-#{pdf_page_number} format
                                div.setAttribute("id", "page-" + (page.pageIndex + 1));

                                // This will keep positions of child elements as per our needs
                                div.setAttribute("style", "position: relative");

                                // Append div within div#container
                                container.appendChild(div);

                                // Create a new Canvas element
                                var canvas = popup.document.createElement("canvas");

                                // Append Canvas within div#page-#{pdf_page_number}
                                div.appendChild(canvas);

                                var context = canvas.getContext('2d');
                                canvas.height = viewport.height;
                                canvas.width = viewport.width;

                                var renderContext = {
                                    canvasContext: context,
                                    viewport: viewport
                                };
                                console.log(",,,,,,,,,,,,,,,,,,,,,,renderContext", renderContext)
                                // Render PDF page
                                page.render(renderContext)
                                    .then(function () {
                                        // Get text-fragments
                                        return page.getTextContent();
                                    })
                                    .then(function (textContent) {
                                        // Create div which will hold text-fragments
                                        var textLayerDiv = popup.document.createElement("div");

                                        // Set it's class to textLayer which have required CSS styles
                                        textLayerDiv.setAttribute("class", "textLayer");

                                        // Append newly created div in `div#page-#{pdf_page_number}`
                                        div.appendChild(textLayerDiv);

                                        // Create new instance of TextLayerBuilder class
                                        
                                        var textLayer = new TextLayerBuilder({
                                            textLayerDiv: textLayerDiv,
                                            pageIndex: page.pageIndex,
                                            viewport: viewport
                                        });

                                        // Set text-fragments
                                        console.log(textContent)
                                        textLayer.setTextContent(textContent);

                                        // Render text-fragments
                                        textLayer.render();
                                    });
                            });

                        }
                    }


                    // function renderPage(num) {
                    //     pageRendering = true;
                    //     // Using promise to fetch the page
                    //     pdfDoc.getPage(num).then(function (page) {
                    //         console.log(page.getViewport(scale))
                    //         var viewport = page.getViewport(scale);
                    //         canvas.height = 700;
                    //         canvas.width = 700;

                    //         // Render PDF page into canvas context
                    //         var renderContext = {
                    //             canvasContext: ctx,
                    //             viewport: viewport
                    //         };
                    //         var renderTask = page.render(renderContext);

                    //         // Wait for rendering to finish
                    //         renderTask.promise.then(function () {
                    //             pageRendering = false;
                    //             if (pageNumPending !== null) {
                    //                 // New page rendering is pending
                    //                 renderPage(pageNumPending);
                    //                 pageNumPending = null;
                    //             }
                    //         });
                    //     });

                    //     // Update page counters
                    //     popup.document.getElementById('page_num').textContent = num;
                    // }
                    // /**
                    //  * If another page rendering in progress, waits until the rendering is
                    //  * finised. Otherwise, executes rendering immediately.
                    //  */
                    // function queueRenderPage(num) {
                    //     if (pageRendering) {
                    //         pageNumPending = num;
                    //     } else {
                    //         renderPage(num);
                    //     }
                    // }

                    // /**
                    //  * Displays previous page.
                    //  */
                    // function onPrevPage() {
                    //     if (pageNum <= 1) {
                    //         return;
                    //     }
                    //     pageNum--;
                    //     queueRenderPage(pageNum);
                    // }
                    // popup.document.getElementById('prev').addEventListener('click', onPrevPage);
                    // /**
                    //  * Displays next page.
                    //  */
                    // function onNextPage() {
                    //     if (pageNum >= pdfDoc.numPages) {
                    //         return;
                    //     }
                    //     pageNum++;
                    //     queueRenderPage(pageNum);
                    // }
                    // popup.document.getElementById('next').addEventListener('click', onNextPage);

                    /**
                     * Asynchronously downloads PDF.
                     */


                    //var PDFJS = null
                    $.getScript(self.session.url('/report_no_download/static/src/js/pdf.js')).done(function (script, statusCode) {
                        //PDFJS = script;
                        //get the worker
                        PDFJS.workerSrc = '/report_no_download/static/src/js/pdf.worker.js'
                        
                        PDFJS.locale = (PDFJS.locale === undefined ? navigator.language : PDFJS.locale);
                        PDFJS.locale = "ar_SY"
                        //PDFJS.worker = script;

                        PDFJS.getDocument(url).then(function (pdfDoc_) {
                            pdfDoc = pdfDoc_;
                            //popup.document.getElementById('page_count').textContent = pdfDoc.numPages;

                            // Initial/first page rendering
                            //renderPage(pageNum);
                            renderPagedoc(pdfDoc);
                        });


                    }).fail(function (x, y, z) {
                        console.log("error..................", x, y, z)
                    })

                    instance.web.unblockUI();

                    return;


                }


                var c = instance.webclient.crashmanager;
                return $.Deferred(function (d) {
                    self.session.get_file({
                        url: '/web/report',
                        data: {
                            action: JSON.stringify(action)
                        },
                        complete: instance.web.unblockUI,
                        success: function () {
                            if (!self.dialog) {
                                cr_options.on_close();
                            }
                            self.dialog_stop();
                            d.resolve();
                        },
                        error: function () {
                            c.rpc_error.apply(c, arguments);
                            d.reject();
                        }
                    })
                });
            });
        },

    });

};
