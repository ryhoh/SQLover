// Functions
const clearUserResult = function() {
    this.user_message = null;
};

const selectSentence = function(lang, dict) {
    for (const key in dict) {
        if (key === lang)
            return dict[key];
    }
    return null;
};

const setUserData = function(response) {
    this.token = response.data.access_token;
    this.user_clear_num = response.data.cleared_num;
    this.cleared_flags = response.data.cleared_flags;
    localStorage.setItem('user_name', this.user_name);
    localStorage.setItem('user_clear_num', this.user_clear_num);
    localStorage.setItem('cleared_flags', this.cleared_flags.map(x => '' + Number(x)).join(''));  // 0010110100010...
    localStorage.setItem('token', this.token);
};

const wipeProblem = function() {
    this.selected_problem = null;
    this.description = null;
    this.tables = null;
    this.expected_records = null;
    this.expected_columns = null;
    this.order_sensitive = null;
};

const wipeSql = function() {
    this.sql = null;
    this.judged = false;
    this.result = null,
    this.answer_columns = null;
    this.answer_records = null;
    this.wrong_line = null;
    this.re_message = null;
};

// c.f. https://qiita.com/ka215/items/d059a78e29adef3978b5
const mb_substr = function(str, begin, end) {
    let ret = '';
    for (let i = 0, len = 0; i < str.length; ++i, ++len) {
        const upper = str.charCodeAt(i);
        const lower = str.length > (i + 1) ? str.charCodeAt(i + 1) : 0;
        let s = '';
        if(0xD800 <= upper && upper <= 0xDBFF && 0xDC00 <= lower && lower <= 0xDFFF) {
            ++i;
            s = String.fromCharCode(upper, lower);
        } else {
            s = String.fromCharCode(upper);
        }
        if (begin <= len && len < end) {
            ret += s;
        }
    }
    return ret;
};


// Vue.js
new Vue({
    el: '#vue_app',
    delimiters: ['${', '}'],
    
    data: () => ({
        language: 'en',

        user_name: null,
        user_password: null,
        user_accessing: null,
        user_info: 'forms',
        user_message: null,
        user_clear_num: null,

        token: null,

        problem_list: null,
        problem_list_errored: false,
        problem_list_loding: false,
        problem_num: null,
        cleared_flags: null,

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
        submit_message: null,
        answer_columns: null,
        answer_records: null,
        wrong_line: null,
        re_message: null,
        sql_submit_error: false,
        sql_submitting: false,
    }),

    computed: {
        isEnglish: function() {
            return this.language === 'en';
        },

        isJapanese: function() {
            return this.language === 'ja';
        },
    },

    methods: {
        signup: function() {
            if (this.user_name === null || this.user_name.length < 4 || 30 < this.user_name.length) {
                this.user_message = selectSentence(this.language, {
                    'ja': 'ユーザ名は4文字以上30文字以内の英数字にしてください',
                    'en': 'Username must be between 4 ~ 30 letters!',
                });
                return
            }

            if (this.user_password === null || this.user_password.length < 8 || 60 < this.user_password.length) {
                this.user_message = selectSentence(this.language, {
                    'ja': 'パスワードは8文字以上60文字以内にしてください',
                    'en': 'Password must be between 8 ~ 60 letters!',
                });
                return
            }

            this.user_accessing = true;
            this.user_message = selectSentence(this.language, {
                'ja': '登録中...',
                'en': 'Registering...',
            });

            const params = new URLSearchParams();
            params.append('name', this.user_name);
            params.append('password', this.user_password);
            axios
                .post('/api/v1/signup', params)
                .then(response => {
                    setTimeout(clearUserResult.bind(this), 5000);
                    if (response.data.result === 'success') {
                        this.user_info = 'loginned';
                        setUserData.bind(this)(response);
                        this.user_message = selectSentence(this.language, {
                            'ja': '登録に成功しました!',
                            'en': 'Successfully registered!',
                        });
                    } else {  // failed
                        this.user_message = selectSentence(this.language, {
                            'ja': '登録に失敗しました（別の名前にしてください）',
                            'en': 'Register failed (use other name)',
                        });
                    }
                })
                .catch(error => {
                    console.error(error.response);
                    this.user_message = selectSentence(this.language, {
                        'ja': 'エラーが発生しました...',
                        'en': 'An error has occurred...',
                    });
                })
                .finally(() => {
                    this.user_accessing = false;
                });
        },

        testProblem: function() {
            this.submit_message = null;
            this.result = 'Judging...';
            this.sql_submitting = true;

            const params = new URLSearchParams();
            params.append('problem_name', mb_substr(this.selected_problem, 1, this.selected_problem.length));
            params.append('answer', this.sql);

            axios
                .post('/api/v1/test', params)
                .then(response => {
                    this.result = response.data.result;
                    this.re_message = response.data.message;
                    this.answer_columns = response.data.answer_columns;
                    this.answer_records = response.data.answer_records;
                    this.wrong_line = response.data.wrong_line;
                })
                .catch(error => {
                    console.error(error.response);
                    this.sql_submit_error = true;
                })
                .finally(() => {
                    this.judged = true;
                    this.sql_submitting = false;
                });
        },

        submitProblem: function() {
            this.submit_message = null;
            if (this.user_info !== 'loginned') {
                this.result = null;
                this.submit_message = selectSentence(this.language, {
                    'ja': '提出するにはログインしてください。',
                    'en': 'Please login to submit answer.',
                });
                return;
            }

            this.result = 'Judging...';
            this.sql_submitting = true;
            axios
                .post(
                    '/api/v1/submit',
                    {
                        'problem_name': mb_substr(this.selected_problem, 1, this.selected_problem.length),
                        'answer': this.sql,
                    },
                    {
                        'headers': { 'Authorization': 'Bearer ' + this.token }
                    }
                )
                .then(response => {
                    this.result = response.data.result;
                    if (this.result === 'AC') {
                        // if (mb_substr(this.selected_problem, 0, 1) === '🏆') {
                        //     this.selected_problem = '🏆' + mb_substr(this.selected_problem, 1, this.selected_problem.length);
                        // }
                        this.submit_message = selectSentence(this.language, {
                            'ja': '提出しました。',
                            'en': 'Submitted.',
                        });
                    } else {
                        this.re_message = response.data.message;
                    }
                    this.answer_columns = response.data.answer_columns;
                    this.answer_records = response.data.answer_records;
                    this.wrong_line = response.data.wrong_line;
                    this.user_clear_num = response.data.cleared_num;
                    this.cleared_flags = response.data.cleared_flags;
                    localStorage.setItem('user_clear_num', this.user_clear_num);
                    localStorage.setItem('cleared_flags', this.cleared_flags.map(x => '' + Number(x)).join(''));  // 0010110100010...
                })
                .catch(error => {
                    console.error(error.response);
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
            params.append('username', this.user_name);
            params.append('password', this.user_password);
            axios
                .post('/api/v1/token', params)
                .then(response => {
                    setTimeout(clearUserResult.bind(this), 5000);
                    this.user_info = 'loginned';
                    setUserData.bind(this)(response);
                    this.user_message = selectSentence(this.language, {
                        'ja': 'ログインに成功しました!',
                        'en': 'Successfully logined!',
                    });
                })
                .catch(error => {
                    console.error(error.response);
                    this.user_message = selectSentence(this.language, {
                        'ja': 'ユーザ名またはパスワードが間違っています',
                        'en': 'Wrong username or password.',
                    });
                })
                .finally(() => {
                    this.user_accessing = false;
                });
        },

        logout: function() {
            this.user_accessing = true;
            this.user_message = selectSentence(this.language, {
                'ja': '処理中...',
                'en': 'Processing...',
            });

            this.token = null;
            localStorage.removeItem('user_name');
            localStorage.removeItem('user_clear_num');
            localStorage.removeItem('cleared_flags');
            localStorage.removeItem('token');
            this.user_name = '';
            this.user_password = '';
            this.cleared_flags = null;
            this.user_info = 'forms';
            setTimeout(clearUserResult.bind(this), 5000);
            this.user_message = selectSentence(this.language, {
                'ja': 'ログアウトしました',
                'en': 'Logout.',
            });
            this.user_accessing = false;
        },

        addTrophyMark: function(problem_name, problem_idx) {
            if (this.cleared_flags == null) {
                return '　' + problem_name;
            }

            if (this.cleared_flags[problem_idx]) {
                return '🏆' + problem_name;
            } else {
                return '　' + problem_name;
            }
        },
    },

    watch: {
        selected_problem: function(new_problem, _old_problem) {
            if (new_problem === null)
                return;  // '-- Please choose problem --'

            new_problem = mb_substr(new_problem, 1, new_problem.length)  // Remove 🏆
            this.problem_loding = true;
            axios
                .get('/api/v1/problem', {
                    params: { problem_name: new_problem }
                })
                .then(response => {
                    // Print new problem's data
                    this.tables = response.data.tables;
                    if (this.language === 'ja' && response.data.description_jp) {
                        this.description = response.data.description_jp;
                    } else {
                        this.description = response.data.description;
                    }
                    this.expected_records = response.data.expected.records;
                    this.expected_columns = response.data.expected.columns;
                    this.order_sensitive = response.data.expected.order_sensitive;

                    // Delete old problem's gabage
                    wipeSql.bind(this)();
                })
                .catch(error => {
                    console.error(error.response);
                    this.problem_errored = true;
                })
                .finally(() => this.problem_loding = false);
        }
    },

    mounted() {
        // Set default language
        this.language = (navigator.browserLanguage || navigator.language || navigator.userLanguage).substr(0,2);
        
        // Load problem list
        this.problem_list_loading = true;
        axios
            .get('/api/v1/problem_list')
            .then(response => {
                this.problem_list = response.data.problems;
                this.problem_num = this.problem_list.length;
            })
            .catch(error => {
                console.error(error.response);
                this.problem_list_errored = true;
            })
            .finally(() => this.problem_list_loading = false);

        // read cookie if available
        if (localStorage.length > 0) {
            this.user_info = 'loginned';
            if (localStorage.getItem('user_name')) this.user_name = localStorage.getItem('user_name');
            if (localStorage.getItem('user_clear_num')) this.user_clear_num = localStorage.getItem('user_clear_num');
            if (localStorage.getItem('cleared_flags')) {
                this.cleared_flags = localStorage.getItem('cleared_flags').split('').map(x => Boolean(Number(x)));
            }
            if (localStorage.getItem('token')) this.token = localStorage.getItem('token');
        }
    },
});
