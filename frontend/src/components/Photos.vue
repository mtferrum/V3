<template>
    <div>
        <v-dialog
                :width="dialogWidth"
                v-model="dialog"
                persistent
        >
            <v-card>
                <v-card-title color="success">
                    <h2 class="title">Вы уверены?</h2>
                    <v-spacer/>
                    <v-btn
                            icon
                            @click="dialog=false"
                    >
                        <v-icon>close</v-icon>
                    </v-btn>
                </v-card-title>
                <v-divider/>
                <v-card-text>
                    <v-layout>
                        <v-spacer/>
                        <v-btn
                                color="error"
                                @click="dialog=false"
                                class="ma-2"
                        >
                            нет
                        </v-btn>
                        <v-btn
                                @click="deletePhoto"
                                color="success"
                                class="ma-2"
                        >
                            да
                        </v-btn>
                        <v-spacer/>
                    </v-layout>
                </v-card-text>
            </v-card>
        </v-dialog>
        <v-layout row wrap justify-center class="px-2">
            <v-card
                    flat
                    tile
                    v-for="entry in photos"
                    class="ma-2"
                    color="grey lighten-2"
                    max-width="300"
            >
                <v-layout justify-end>
                    <v-btn @click="openDeleteDialog(entry)" icon>
                        <v-icon color="red">delete</v-icon>
                    </v-btn>
                </v-layout>
                <v-img
                        align="center"
                        justify="center"
                        contain
                        class="px-2 pb-2"
                        :src="$store.state.imagesUrl + entry[1]"
                        :lazy-src="require('@/assets/placeholder.jpeg')"
                ></v-img>
            </v-card>
        </v-layout>
    </div>

</template>

<script>
    export default {
        name: 'Photos',
        data: () => ({
            dialog: false,
            photos: []
        }),
        methods: {
            getPhotos() {
                let request = new XMLHttpRequest();
                let self = this;
                request.onreadystatechange = function () {
                    if (request.readyState === 4 && request.status >= 200 && request.status < 300) {
                        self.photos = JSON.parse(request.response)
                    } else if (request.readyState === 4) {
                        console.error("error", {status: request.status, msg: request.response});
                    }
                };
                let url = this.$store.state.apiUrl + "photo";
                if (this.currentSection === "whitelist") {
                    url = this.$store.state.apiUrl + "tester_photo"
                }

                request.open("GET", url, true);
                request.send();
            },
            openDeleteDialog(data) {
                this.photoToDelete = data;
                this.dialog = true;
            },
            deletePhoto() {
                let data = this.photoToDelete;
                let request = new XMLHttpRequest();
                let self = this;
                request.onreadystatechange = function () {
                    if (request.readyState === 4 && request.status >= 200 && request.status < 300) {
                        self.getPhotos()
                    } else if (request.readyState === 4) {
                        console.error("error", {status: request.status, msg: request.response});
                        self.getPhotos()
                    }
                }
                let url = this.$store.state.apiUrl + "photo?id=" + data[0] + "&label_id=" + data[2] + "&filename=" + data[1];
                request.open("DELETE", url, true);
                request.send();
                self.dialog = false;
            }
        },
        beforeMount() {
            this.getPhotos()
        },
        computed: {
            // Adjust component width for mobile devices
            dialogWidth() {
                switch (this.$vuetify.breakpoint.name) {
                    case 'xs':
                        return '80%';
                    case 'sm':
                        return '80%';
                    case 'md':
                        return '20%';
                    case 'lg':
                        return '20%';
                    case 'xl':
                        return '20%';
                }
            },
            currentSection() {
                return this.$store.getters.currentSection
            }
        },
        watch: {
            currentSection: function (val) {
                this.getPhotos()
            },
        }
    }
</script>

