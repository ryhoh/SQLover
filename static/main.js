// Vue.js
const vm = new Vue({
    el: '#vue_app',
    
    data: () => ({
        language: 'en',

        problem_list: null,
        problem_list_errored: false,
        problem_list_loding: false,

        selected_problem: null,
        description: null,
        tables: null,
        expected_records: null,
        expected_columns: null,
        order_sensitive: null,
        problem_errored: false,
        problem_loding: false,
        
        sql: null,
        judged: false,
        result: null,
        answer_columns: null,
        answer_records: null,
        wrong_line: null,
        re_message: null,
        sql_submit_error: false,
        sql_submitting: false,
    }),

    computed: {
        is_english: function() {
            return this.language === 'en';
        },

        is_japanese: function() {
            return this.language === 'ja';
        },
    },

    methods: {
        submit_problem: function() {
            this.result = 'Judging...';
            this.sql_submitting = true;

            const params = new URLSearchParams();
            params.append('problem_name', this.selected_problem);
            params.append('answer', this.sql);
            axios
                .post('/api/v1/submit', params)
                .then(response => {
                    this.result = response.data.result;
                    this.re_message = response.data.message;
                    this.answer_columns = response.data.answer_columns;
                    this.answer_records = response.data.answer_records;
                    this.wrong_line = response.data.wrong_line;
                })
                .catch(error => {
                    console.log(error.response);
                    this.sql_submit_error = true;
                })
                .finally(() => {
                    this.judged = true;
                    this.sql_submitting = false;
                });
        },
    },

    watch: {
        selected_problem: function(new_problem, old_problem) {
            this.problem_loding = true;
            axios
                .get('/api/v1/problem', {
                    params: {
                        problem_name: new_problem,
                    }
                })
                .then(response => {
                    this.tables = response.data.tables;
                    this.description = response.data.description;
                    this.expected_records = response.data.expected.records;
                    this.expected_columns = response.data.expected.columns;
                    this.order_sensitive = response.data.expected.order_sensitive;
                })
                .catch(error => {
                    console.log(error.response);
                    this.problem_errored = true;
                })
                .finally(() => this.problem_loding = false);
        }
    },

    mounted() {
        // Load problem list
        this.problem_list_loading = true;
        axios
            .get('/api/v1/problem_list')
            .then(response => {
                this.problem_list = response.data.problems;
                this.problem_list.sort();
            })
            .catch(error => {
                console.log(error.response);
                this.problem_list_errored = true;
            })
            .finally(() => this.problem_list_loading = false);

        // Set default language
        this.language = (navigator.browserLanguage || navigator.language || navigator.userLanguage).substr(0,2);
    },
});
