// Functions
const clearUserResult = function() {
    this.user_message = null;
};


// Vue.js
const vm = new Vue({
    el: '#vue_app',
    
    data: () => ({
        language: 'en',

        user_name: null,
        user_password: null,
        user_accessing: null,
        user_info: 'forms',
        user_message: null,
        user_clear_num: null,

        problem_list: null,
        problem_list_errored: false,
        problem_list_loding: false,
        problem_num: null,

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
        signup: function() {
            if (this.user_name === null || this.user_name.length < 4 || 30 < this.user_name.length) {
                if (this.language === 'ja') {
                    this.user_message = 'ユーザ名は4文字以上30文字以内の英数字にしてください';
                } else {
                    this.user_message = 'Username must be between 4 ~ 30 letters!';
                }
                return
            }

            if (this.user_password === null || this.user_password.length < 8 || 60 < this.user_password.length) {
                if (this.language === 'ja') {
                    this.user_message = 'パスワードは8文字以上60文字以内にしてください';
                } else {
                    this.user_message = 'Password must be between 8 ~ 60 letters!';
                }
                return
            }

            this.user_accessing = true;
            if (this.language === 'ja') {
                this.user_message = '登録中...';
            } else {
                this.user_message = 'Registering...';
            }

            const params = new URLSearchParams();
            params.append('name', this.user_name);
            params.append('password', this.user_password);
            axios
                .post('/api/v1/signup', params)
                .then(response => {
                    setTimeout(clearUserResult.bind(this), 5000);
                    if (response.data.result === 'success') {
                        this.user_info = 'loginned';
                        this.user_clear_num = response.data.cleared_num;
                        if (this.language === 'ja') {
                            this.user_message = '登録に成功しました!';
                        } else {
                            this.user_message = 'Successfully registered!';
                        }
                    } else {  // failed
                        if (this.language === 'ja') {
                            this.user_message = '登録に失敗しました（別の名前にしてください）';
                        } else {
                            this.user_message = 'Register failed (use other name)';
                        }
                    }
                })
                .catch(error => {
                    console.log(error.response);
                    if (this.language === 'ja') {
                        this.user_message = 'エラーが発生しました...';
                    } else {
                        this.user_message = 'An error has occurred...';
                    }
                })
                .finally(() => {
                    this.user_accessing = false;
                });
        },

        submit_problem: function() {
            this.result = 'Judging...';
            this.sql_submitting = true;

            const params = new URLSearchParams();
            params.append('problem_name', this.selected_problem);
            params.append('answer', this.sql);
            if (this.user_info === 'loginned') {
                params.append('user_name', this.user_name);
                params.append('user_passwd', this.user_password);
            }

            axios
                .post('/api/v1/submit', params)
                .then(response => {
                    this.result = response.data.result;
                    this.re_message = response.data.message;
                    this.answer_columns = response.data.answer_columns;
                    this.answer_records = response.data.answer_records;
                    this.wrong_line = response.data.wrong_line;
                    this.user_clear_num = response.data.cleared_num;
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

        login: function() {
            this.user_accessing = true;

            const params = new URLSearchParams();
            params.append('name', this.user_name);
            params.append('password', this.user_password);
            axios
                .post('/api/v1/login', params)
                .then(response => {
                    setTimeout(clearUserResult.bind(this), 5000);
                    this.user_info = 'name';
                    this.user_clear_num = response.data.cleared_num;
                    if (response.data.result === 'success') {
                        this.user_info = 'loginned';
                        if (this.language === 'ja') {
                            this.user_message = 'ログインに成功しました!';
                        } else {
                            this.user_message = 'Successfully logined!';
                        }
                    } else {  // failed
                        if (this.language === 'ja') {
                            this.user_message = 'ユーザ名またはパスワードが間違っています';
                        } else {
                            this.user_message = 'Wrong username or password.';
                        }
                    }
                })
                .catch(error => {
                    console.log(error.response);
                    if (this.language === 'ja') {
                        this.user_message = 'エラーが発生しました...';
                    } else {
                        this.user_message = 'An error has occurred...';
                    }
                })
                .finally(() => {
                    this.user_accessing = false;
                });
        },

        logout: function() {
            this.user_accessing = true;
            if (this.language === 'ja') {
                this.user_message = '処理中...';
            } else {
                this.user_message = 'Processing...';
            }

            this.user_name = '';
            this.user_password = '';
            this.user_info = 'forms';
            setTimeout(clearUserResult.bind(this), 5000);
            if (this.language === 'ja') {
                this.user_message = 'ログアウトしました';
            } else {
                this.user_message = 'Logout.';
            }
            
            this.user_accessing = false;
        },
    },

    watch: {
        selected_problem: function(new_problem, _old_problem) {
            this.problem_loding = true;
            axios
                .get('/api/v1/problem', {
                    params: {
                        problem_name: new_problem,
                    }
                })
                .then(response => {
                    // Print new problem's data
                    this.tables = response.data.tables;
                    this.description = response.data.description;
                    this.expected_records = response.data.expected.records;
                    this.expected_columns = response.data.expected.columns;
                    this.order_sensitive = response.data.expected.order_sensitive;

                    // Delete old problem's gabage
                    this.sql = null;
                    this.judged = false;
                    this.result = null,
                    this.answer_columns = null;
                    this.answer_records = null;
                    this.wrong_line = null;
                    this.re_message = null;
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
                this.problem_num = this.problem_list.length;
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
