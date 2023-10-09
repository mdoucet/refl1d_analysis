new Vue({
    el: '#app',
    data: {
        sortedLayers: [],
        dictionaryLoaded: false,
        },
    methods: {
        process() {
            // Sort. We should also reassign layer numbers so that it's nice and
            // doesn't skip numbers.
            this.sortedLayers.sort((a, b) => a['order'] - b['order']);

        },
        async loadDictionary() {
            try {
                const response = await fetch('http://localhost:3000/api/testdata');
                const data = await response.json();
                this.sortedLayers = data['models'][0]['sample']['layers'];
                for (const [index, item] of Object.entries(this.sortedLayers)) {
                    item['order'] = index;
                }
                this.dictionaryLoaded = true;
            } catch (error) {
                console.error(error);
            }
        },
        addLayer() {
            // TODO: Implement a better way to create a default layer so
            // that it's complete when we give it back to refl1d.
            const newLayer = {
                "name": "New Layer",
                "order": 1000,
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
            this.sortedLayers.push(newLayer);
        }
    }
});
