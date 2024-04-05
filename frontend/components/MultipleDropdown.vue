<script>
export default {
    props: {
        options: {
            type: Array,
            required: true,
        },
        valueName: {
            type: String,
            required: true,
        },
    },

    data() {
        return {
            isDropdownOpen: false,
            selectedOptions: [],
            // selectedOptions: alreadySelectedOptions ? alreadySelectedOptions.slice() : [],
        };
    },

    computed: {
        buttonText() {
            return this.selectedOptions.length > 0 ? `${this.valueName}: ${this.selectedOptions.join(', ')}` : `Select ${this.valueName}`;
        }
    },
    methods: {
        toggleDropdown() {
            this.isDropdownOpen = !this.isDropdownOpen;
        },

        toggleOption(optionValue) {
            if (this.selectedOptions.includes(optionValue)) {
                this.selectedOptions = this.selectedOptions.filter(option => option !== optionValue);
            } else {
                this.selectedOptions.push(optionValue);
            }
            this.$emit('update:selectedOptions', this.selectedOptions);
        }
    }
};
</script>


<template>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">
    <div class="container">
        <div class="select-btn" @click="toggleDropdown">
            <span class="btn-text">{{ buttonText }}</span>
            <span class="arrow-dwn">
                <i v-if="!isDropdownOpen" class="fa-solid fa-chevron-down"></i>
                <i v-if="isDropdownOpen" class="fa-solid fa-chevron-up"></i>
            </span>
        </div>
        <ul v-if="isDropdownOpen" class="form-control mt-2" style="
            border-radius: 2px;
            border: 2px dashed var(--colour-panel-hard);
        ">
            <li v-for="(option, index) in options" :key="index" :value="option.value" 
                @click="toggleOption(option.value)" 
                :class="{ checked: selectedOptions.includes(option.value) }" 
                class="item">
                <i v-if="selectedOptions.includes(option.value)" class="fa-solid fa-check check-icon"></i>
                <span class="item-text">{{ option.label }}</span>
            </li>
        </ul>
    </div>
</template>