<template>
    <v-app>
        <v-navigation-drawer
                app
                v-model="drawer"
                temporary
        >
            <v-list dense active-class="pink--text">
                <template v-for="(section, key) in sections">
                    <v-list-item
                            @click.stop="switchSection(key)"
                            :input-value="$store.getters.currentSection === key"

                    >
                        <v-list-item-content>
                            <v-list-item-title>{{section.name.toUpperCase()}}</v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                </template>
            </v-list>
        </v-navigation-drawer>
        <v-app-bar
                app
                color="primary"
                dark
        >
            <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
            <span class="headline">{{sections[$store.getters.currentSection].name.toUpperCase()}}</span>
            <v-layout justify-end>
                <send-photos-form @success="refreshPhotos"></send-photos-form>
            </v-layout>

        </v-app-bar>
        <v-content>

            <photos ref="photos"></photos>
        </v-content>
    </v-app>
</template>

<script>
    import SendPhotosForm from "@/components/SendPhotosForm"
    import Photos from "@/components/Photos"

    export default {
        name: 'App',
        components: {
            SendPhotosForm,
            Photos
        },
        data: () => ({
            drawer: false,
            sections: {
                "blacklist": {
                    "name": "Чёрный список",
                },
                "whitelist": {
                    "name": "Белый список"
                }
            }
        }),
        methods: {
            refreshPhotos() {
                this.$refs.photos.getPhotos()
            },
            switchSection(section) {
                this.$store.state.currentSection = section;
                localStorage.setItem('currentSection', section);
                this.drawer = false;
            }
        },
        mounted() {
            let section = localStorage.getItem('currentSection');
            if (section) {
                this.$store.state.currentSection = section;
            }
            this.$store.dispatch("setVersion", null);
        }
    };
</script>
