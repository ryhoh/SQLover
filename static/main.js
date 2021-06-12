const clearUserResult=function(){this.user_message=null},selectSentence=function(e,s){for(const t in s)if(t===e)return s[t];return null},setCurrentProblem=function(e){this.tables=e.tables,"ja"===this.language&&e.description_jp?this.description=e.description_jp:this.description=e.description,this.expected_records=e.expected.records,this.expected_columns=e.expected.columns,this.order_sensitive=e.expected.order_sensitive},setUserData=function(e){this.token=e.data.access_token,this.user_clear_num=e.data.cleared_num,this.cleared_flags=e.data.cleared_flags,localStorage.setItem("user_name",this.user_name),localStorage.setItem("user_clear_num",this.user_clear_num),localStorage.setItem("cleared_flags",this.cleared_flags.map(e=>""+Number(e)).join("")),localStorage.setItem("token",this.token)},wipeProblem=function(){this.selected_problem=null,this.description=null,this.tables=null,this.expected_records=null,this.expected_columns=null,this.order_sensitive=null},wipeSql=function(){this.sql=null,this.judged=!1,this.result=null,this.answer_columns=null,this.answer_records=null,this.wrong_line=null,this.re_message=null},mb_substr=function(e,s,t){let l="";for(let r=0,n=0;r<e.length;++r,++n){const a=e.charCodeAt(r),i=e.length>r+1?e.charCodeAt(r+1):0;let o="";55296<=a&&a<=56319&&56320<=i&&i<=57343?(++r,o=String.fromCharCode(a,i)):o=String.fromCharCode(a),s<=n&&n<t&&(l+=o)}return l};new Vue({el:"#vue_app",delimiters:["${","}"],data:()=>({language:"en",user_name:null,user_password:null,user_accessing:null,user_info:"forms",user_message:null,user_clear_num:null,token:null,problem_list:null,problem_list_errored:!1,problem_list_loding:!1,problem_num:null,cleared_flags:null,problems_cache:{},selected_problem:null,description:null,tables:null,expected_records:null,expected_columns:null,order_sensitive:null,problem_errored:!1,problem_loding:!1,sql:null,judged:!1,result:null,submit_message:null,answer_columns:null,answer_records:null,wrong_line:null,re_message:null,sql_submit_error:!1,sql_submitting:!1}),computed:{isEnglish:function(){return"en"===this.language},isJapanese:function(){return"ja"===this.language}},methods:{testProblem:function(){this.submit_message=null,this.result="Judging...",this.sql_submitting=!0;const e=new URLSearchParams;e.append("problem_name",mb_substr(this.selected_problem,1,this.selected_problem.length)),e.append("answer",this.sql),axios.post("/api/v1/test",e).then(e=>{this.result=e.data.result,this.re_message=e.data.message,this.answer_columns=e.data.answer_columns,this.answer_records=e.data.answer_records,this.wrong_line=e.data.wrong_line}).catch(e=>{console.error(e.response),this.sql_submit_error=!0}).finally(()=>{this.judged=!0,this.sql_submitting=!1})},submitProblem:function(){if(this.submit_message=null,"loginned"!==this.user_info)return this.result=null,void(this.submit_message=selectSentence(this.language,{ja:"提出するにはログインしてください。",en:"Please login to submit answer."}));this.result="Judging...",this.sql_submitting=!0,axios.post("/api/v1/submit",{problem_name:mb_substr(this.selected_problem,1,this.selected_problem.length),answer:this.sql},{headers:{Authorization:"Bearer "+this.token}}).then(e=>{this.result=e.data.result,"AC"===this.result?this.submit_message=selectSentence(this.language,{ja:"提出しました。",en:"Submitted."}):this.re_message=e.data.message,this.answer_columns=e.data.answer_columns,this.answer_records=e.data.answer_records,this.wrong_line=e.data.wrong_line,this.user_clear_num=e.data.cleared_num,this.cleared_flags=e.data.cleared_flags,localStorage.setItem("user_clear_num",this.user_clear_num),localStorage.setItem("cleared_flags",this.cleared_flags.map(e=>""+Number(e)).join(""))}).catch(e=>{console.error(e.response),this.sql_submit_error=!0}).finally(()=>{this.judged=!0,this.sql_submitting=!1})},login:function(){this.user_accessing=!0;const e=new URLSearchParams;e.append("username",this.user_name),e.append("password",this.user_password),axios.post("/api/v1/token",e).then(e=>{setTimeout(clearUserResult.bind(this),5e3),this.user_info="loginned",setUserData.bind(this)(e),this.user_message=selectSentence(this.language,{ja:"ログインに成功しました!",en:"Successfully logined!"})}).catch(e=>{console.error(e.response),this.user_message=selectSentence(this.language,{ja:"ユーザ名またはパスワードが間違っています",en:"Wrong username or password."})}).finally(()=>{this.user_accessing=!1})},logout:function(){this.user_accessing=!0,this.user_message=selectSentence(this.language,{ja:"処理中...",en:"Processing..."}),this.token=null,localStorage.removeItem("user_name"),localStorage.removeItem("user_clear_num"),localStorage.removeItem("cleared_flags"),localStorage.removeItem("token"),this.user_name="",this.user_password="",this.cleared_flags=null,this.user_info="forms",setTimeout(clearUserResult.bind(this),5e3),this.user_message=selectSentence(this.language,{ja:"ログアウトしました",en:"Logout."}),this.user_accessing=!1},addTrophyMark:function(e,s){return null!=this.cleared_flags&&this.cleared_flags[s]?"🏆"+e:"　"+e}},watch:{selected_problem:function(e,s){null!==e&&((e=mb_substr(e,1,e.length))in this.problems_cache?setCurrentProblem.bind(this)(this.problems_cache[e]):(this.problem_loding=!0,axios.get("/api/v1/problem",{params:{problem_name:e}}).then(s=>{setCurrentProblem.bind(this)(s.data),this.problems_cache[e]=s.data,wipeSql.bind(this)()}).catch(e=>{console.error(e.response),this.problem_errored=!0}).finally(()=>this.problem_loding=!1)))}},mounted(){this.language=navigator.language.substr(0,2),this.problem_list_loading=!0,axios.get("/api/v1/problem_list").then(e=>{this.problem_list=e.data.problems,this.problem_num=this.problem_list.length}).catch(e=>{console.error(e.response),this.problem_list_errored=!0}).finally(()=>this.problem_list_loading=!1),localStorage.length>0&&(this.user_info="loginned",localStorage.getItem("user_name")&&(this.user_name=localStorage.getItem("user_name")),localStorage.getItem("user_clear_num")&&(this.user_clear_num=localStorage.getItem("user_clear_num")),localStorage.getItem("cleared_flags")&&(this.cleared_flags=localStorage.getItem("cleared_flags").split("").map(e=>Boolean(Number(e)))),localStorage.getItem("token")&&(this.token=localStorage.getItem("token")))}});