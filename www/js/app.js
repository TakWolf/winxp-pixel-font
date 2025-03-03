import { createApp } from './vue.esm-browser.prod.js'
import db from '../fonts/db.js'

createApp({
    data() {
        return {
            infos: db,
            fontFamily: 'MingLiU',
            fontSize: 16,
            input: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcdefghijklmnopqrstuvwxyz\n0123456789 !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~￥\n\n我们度过的每个平凡的日常，也许就是连续发生的奇迹。',
        }
    },
    computed: {
        infoMap() {
            const map = {}
            for (const info of this.infos) {
                map[info['family_name']] = info
            }
            return map
        },
        fontStyle() {
            return {
                fontFamily: `"${this.fontFamily} ${this.fontSize}px"`,
                fontSize: `${this.fontSize * 2}px`,
            }
        },
    },
    methods: {
        onFontFamilyChange() {
            this.fontSize = this.infoMap[this.fontFamily]['font_sizes'][0]
        },
    },
}).mount('#app')
