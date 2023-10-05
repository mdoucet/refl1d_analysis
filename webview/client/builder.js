import testData from './test-data.js';

new Vue({
    el: '#app',
    data: {
        dictionary: {"sample": {"layers": 
        [{"name": "THF",
            "thickness": {"name": "THF thickness", "slot": {"value": 0}, "fixed": true, "limits": [0.0, "inf"], "bounds": null}, 
            "interface": {"name": "THF interface", "fixed": false, "slot": {"value": 43.77}, "limits": [0.0, "inf"], "bounds": [25.0, 150.0]},
            "magnetism": null, 
            "material": {"name": "THF", "rho": {"name": "THF rho", "fixed": true, "slot": {"value": 6.13}, "limits": ["-inf", "inf"], "bounds": null}, 
                                        "irho": {"name": "THF irho", "fixed": true, "slot": {"value": 0.0}, "limits": ["-inf", "inf"], "bounds": null}}
        }, 
            {"name": "Cu", 
            "thickness": {"name": "Cu thickness", "fixed": false, "slot": {"value": 566.1 }, "limits": [0.0, "inf"], "bounds": [10.0, 800.0]},
            "interface": {"name": "Cu interface", "fixed": false, "slot": {"value": 9.736}, 
            "limits": [0.0, "inf"], "bounds": [8.0, 15.0]}, 
            "magnetism": null, 
            "material": {"name": "Cu", "rho": {"name": "Cu rho", "fixed": true, 
            "slot": {"value": 6.446 }, "limits": ["-inf", "inf"], "bounds": null}, 
            "irho": {"name": "Cu irho", "fixed": true, "slot": {"value": 0.0 }, 
            "limits": ["-inf", "inf"], "bounds": null}}
            }, 
            {"name": "Ti",
            "thickness": {"name": "Ti thickness", "fixed": false, "slot": {"value": 52.91}, "limits": [0.0, "inf"], "bounds": [20.0, 60.0]},
            "interface": {"name": "Ti interface", "fixed": false, "slot": {"value": 12.7}, "limits": [0.0, "inf"], "bounds": [1.0, 20.0]},
            "magnetism": null,
            "material": {"name": "Ti", "rho": {"name": "Ti rho", "fixed": false, "slot": {"value": -1.238}, "limits": ["-inf", "inf"], "bounds": [-2.0, 0.0]},
            "irho": {"name": "Ti irho", "fixed": true, "slot": {"value": 0.0}, "limits": ["-inf", "inf"], "bounds": null}},
            },
            {"name": "Si", "thickness": {"name": "Si thickness", "fixed": true, "slot": {"value": 0 }, "limits": [0.0, "inf"], "bounds": null},
            "interface": {"name": "Si interface", "fixed": true, "slot": {"value": 0 }, "limits": [0.0, "inf"], "bounds": null},
            "magnetism": null, "material": {"name": "Si", "rho": {"name": "Si rho", "fixed": true, "slot": {"value": 2.07}, "limits": ["-inf", "inf"], "bounds": null},
            "irho": {"name": "Si irho", "fixed": true, "slot": {"value": 0.0 }, "limits": ["-inf", "inf"], "bounds": null}},
            }]}
        },
        dictionaryLoaded: false,
        },
    computed: {
        sortedStack() {
            // Create an array of key-value pairs, sort by key, and convert back to an object
            return Object.fromEntries(Object.entries(this.dictionary['sample']['layers']).sort((a, b) => a[0].localeCompare(b[0])));
        }
    },
    methods: {
        process() {

        },
        prepareData() {
            this.sortedLayers = this.dictionary['sample']['layers'];
            for (const [index, item] of Object.entries(this.sortedLayers)) {
                item['order'] = index;
            }
            this.dictionaryLoaded = true;
        },
        loadDictionary() {
            this.dictionary = testData;
            this.dictionaryLoaded = true;
        },
        addLayer() {
            const newLayer = {
                "name": "New Layer",
                "thickness": {
                    "name": "New Layer thickness",
                    "slot": {
                        "value": 0
                    },
                    "fixed": true,
                    "limits": [0.0, "inf"],
                    "bounds": null
                },
                "interface": {
                    "name": "New Layer interface",
                    "fixed": false,
                    "slot": {
                        "value": 0
                    },
                    "limits": [0.0, "inf"],
                    "bounds": [0.0, 100.0]
                },
                "magnetism": null,
                "material": {
                    "name": "New Layer Material",
                    "rho": {
                        "name": "New Layer rho",
                        "fixed": true,
                        "slot": {
                            "value": 0
                        },
                        "limits": ["-inf", "inf"],
                        "bounds": null
                    },
                    "irho": {
                        "name": "New Layer irho",
                        "fixed": true,
                        "slot": {
                            "value": 0
                        },
                        "limits": ["-inf", "inf"],
                        "bounds": null
                    }
                }
            };
            this.dictionary['sample']['layers'].push(newLayer);
        }
    }
});
