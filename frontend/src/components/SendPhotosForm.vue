<template>
    <v-dialog
            :width="dialogWidth"
            v-model="dialog"
            persistent
    >
        <template v-slot:activator="{ on }">
            <v-btn slot="activator" v-on="on">Загрузить</v-btn>
        </template>
        <v-card>
            <v-card-title>
                Загрузить фото
                <v-spacer/>
                <v-btn
                        icon
                        @click.stop="closeDialog"
                >
                    <v-icon>close</v-icon>
                </v-btn>
            </v-card-title>
            <v-form>
                <input
                        multiple
                        type="file"
                        ref="photosInput"
                        style="display:none"
                        name="files"
                        accept="image/jpeg"
                        @change="onFilesPicked"
                >
                <v-row justify-center>
                    <v-col v-for="[imageUrl, name] in previews">
                        <div v-if="files.length || name in errors" class="ma-2">
                            <v-img max-width="200" :src="imageUrl"></v-img>
                            <p class="d-inline-block text-truncate"
                               style="max-width: 200px;"
                            >{{name}}</p>
                            <span v-if="name in errors">{{errors[name]}}</span>
                        </div>
                    </v-col>
                </v-row>
                <v-layout justify-center>
                    <v-btn color="warning" class="ma-2" @click="clickPhotosInput">Добавить</v-btn>
                    <v-btn :disabled="!files.length" color="success" class="ma-2" @click="sendFiles">Загрузить</v-btn>
                </v-layout>
            </v-form>
        </v-card>
    </v-dialog>
</template>

<script>
    export default {
        name: 'SendPhotosForm',

        data: () => ({
            dialog: false,
            files: [],
            previews: [],
            errors: {},
        }),
        methods: {
            clickPhotosInput() {
                this.files = [];
                this.previews = [];
                this.errors = [];
                this.$refs.photosInput.click()
            },
            onFilesPicked(e) {
                let files = e.target.files;
                this.files = files;
                this.preparePreviews(files);
                this.resetInput();
            },
            preparePreviews(files) {
                let self = this;
                self.previews = [];
                for (let file of files) {
                    let fr = new FileReader();
                    fr.readAsDataURL(file);
                    fr.onload = function (e) {
                        self.previews.push([e.target.result, file.name])
                    };
                }
            },
            resetInput() {
                const input = this.$refs.photosInput;
                input.type = 'text';
                input.type = 'file';
            },
            sendFiles() {
                let request = new XMLHttpRequest(),
                    formData = new FormData();
                let url = this.$store.state.apiUrl + "photo"
                if (this.$store.getters.currentSection == "whitelist") {
                    url = this.$store.state.apiUrl + "tester_photo"
                }

                request.open("POST", url);

                let headers = Object.assign({}, this.headers);
                if (!Object.keys(headers).includes("Accept")) {
                    headers["Accept"] = 'application/json'
                }
                if (!Object.keys(headers).includes("Cache-Control")) {
                    headers["Cache-Control"] = 'no-cache'
                }
                if (!Object.keys(headers).includes("X-Requested-With")) {
                    headers["X-Requested-With"] = 'XMLHttpRequest'
                }
                for (let i = 0; i < this.files.length; i++) {
                    formData.append(i, this.files[i]);
                }
                request.send(formData);
                let self = this;
                request.onreadystatechange = function () {
                    if (request.readyState === 4 && request.status >= 200 && request.status < 300) {
                        self.files = [];
                        self.$emit("success", {"response": request.response, "status": request.status})
                        if (request.status == 207) {
                            self.errors = JSON.parse(request.response)["error"]
                        } else {
                            self.closeDialog()
                        }
                    } else if (request.readyState === 4) {
                        console.error("error", {status: request.status, msg: request.responseText});
                        self.$emit("error", {status: request.status, msg: request.responseText});
                        self.closeDialog()
                    }
                }
            },
            closeDialog() {
                this.files = [];
                this.previews = [];
                this.errors = [];
                this.dialog = false;
            }
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
                        return '30%';
                    case 'lg':
                        return '30%';
                    case 'xl':
                        return '30%';
                }
            },
        }
    }
</script>
