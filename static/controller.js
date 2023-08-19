function showLoading() {
    // get timesボタンを隠す
    const getTimes = document.getElementById('getTimes');
    getTimes.style.display = 'none';
    // ローディング用のgifを表示する
    const loadingDiv = document.getElementById('loading');
    loadingDiv.innerHTML = 'データを読み込んでいます...<img src="static/loading.gif" alt="loading_icon">';
}

function hideLoading() {
    // loading用のgifを隠す
    const loadingDiv = document.getElementById('loading');
    loadingDiv.style.display = 'none';
    // ヘッダー画面を隠す(タイトル画面)
    const header = document.getElementById('header');
    header.style.display = 'none';}

function hideLoadingError(error) {
    // loading用のgifを消し、エラーの旨を返す
    const loadingDiv = document.getElementById('loading');
    loadingDiv.innerHTML = `<p>読み込みでエラーが発生しました。</p><p>再読み込みしてください。</p><p>${error}</p>`;
    loadingDiv.style.display = 'block';
    // get timesボタンをもとに戻す
    const getTimes = document.getElementById('getTimes');
    getTimes.style.display = 'block';
}

function get_times() {
    // ローディング画面を表示
    showLoading();

    // Fast API側へリクエストを投げる
    const param  = {
        method: "GET",
        headers: {
            "Content-Type": "application/json; charset=utf-8"
        }
    };

    fetch(`${location.origin}/message`, param)
    .then((res)=>{
        if (!res.ok) {
            // HTTP500等のエラーの場合はエラーを返す
            throw new Error(`HTTP error! Status: ${res.status}`);
        }
        return res.json();
    })
    .then((json)=>{
        // 読み上げ原稿をconsoleに表示する
        console.log(json.text)

        // ローディング画面を消す
        hideLoading();

        // 情報画面にHTMLを埋め込む
        const data = document.getElementById("timesdata");
        data.innerHTML = `
        <div class="left-side">
            <div><h3>現在時刻 (情報取得時刻)</h3></div>
                <div><h2 class="today">${json.today_with_time}</h2></div>
            <div><h3>天気情報</h3></div>
            <div class="container">
                <div class="weather-side1">
                    <div class="weather-gradient"></div>
                    <div class="date-container">
                        <h2 class="date-dayname">今日</h2><span class="date-day">${json.today}</span>
                        <i class="location-icon" data-feather="map-pin"></i><span class="location">${json.weather_info.location}</span>
                    </div>
                    <div class="weather-container"><i class="weather-icon"><img src="${json.weather_info.today_mark}" alt="image"></i>
                        <h1 class="weather-temp">${json.weather_info.today_temp}℃</h1>
                        <h3 class="weather-desc">${json.weather_info.today_weather}</h3>
                    </div>
                </div>
                <div class="weather-side2">
                    <div class="weather-gradient"></div>
                    <div class="date-container">
                        <h2 class="date-dayname">明日</h2><span class="date-day">${json.tomorrow}</span>
                        <i class="location-icon" data-feather="map-pin"></i><span class="location">${json.weather_info.location}</span>
                    </div>
                    <div class="weather-container"><i class="weather-icon"><img src="${json.weather_info.tomorrow_mark}" alt="image"></i>
                        <h1 class="weather-temp">${json.weather_info.tomorrow_temp}℃</h1>
                        <h3 class="weather-desc">${json.weather_info.tomorrow_weather}</h3>
                    </div>
                </div>
            </div>
            <div><h3>為替情報</h3></div>
            <div><ul class="exchange-rate-info">
                <li class="exchange-rate-info-list"><h3>${json.exchange_rate1_info.name} / 円：${json.exchange_rate1_info.exchange_rate}円</h3></li>
                <li class="exchange-rate-info-list"><h3>${json.exchange_rate2_info.name} / 円：${json.exchange_rate2_info.exchange_rate}円</h3></li>
            </ul></div>
            <div><h3>遅延情報</h3></div>
            <div><ul class="train-operation-info">
                <li class="train-operation-info-red"><h3>${json.train_operation_info.suspend_list.length === 0
                ? "✕ 運転見合わせ路線：なし"
                : "✕ 運転見合わせ路線：" + json.train_operation_info.suspend_list.join("、")}</h3></li>
                <li class="train-operation-info-blue"><h3>${json.train_operation_info.delay_list.length === 0
                    ? "△ 遅延路線：なし"
                    : "△ 遅延路線：" + json.train_operation_info.delay_list.join("、")}</h3></li>
                <li class="train-operation-info-yellow"><h3>${json.train_operation_info.trouble_list.length === 0
                    ? "！ お知らせのある路線：なし"
                    : "！ お知らせのある路線：" + json.train_operation_info.trouble_list.join("、")}</h3></li>
            </ul></div>
            <div><h3>主要ニュース</h3></div>
            <div><h3 class="news-info">${Object.values(json.news_info.news_list).map(name => `「${name}」\n`).join('')}</h3></div>
        </div>
        <div class="right-side">
            <div><h3>${json.stock_price1_info.stock_price_name}株価</h3>
                <div class="stock-price-info">
                    <h2 class="latestClosePrice">${json.stock_price1_info.latest_close_price}円</h2>
                    <p>前日比${json.stock_price1_info.percentage_change} (${json.stock_price1_info.latest_close_price_date}現在)</p>
                </div>
                <div><img src="${json.stock_price1_info.stock_price_image}" alt="Image"></div>
            </div>
            <div><h3>${json.stock_price2_info.stock_price_name}株価</h3>
                <div class="stock-price-info">
                    <h2 class="latestClosePrice">${json.stock_price2_info.latest_close_price}円</h2>
                    <p>前日比${json.stock_price2_info.percentage_change} (${json.stock_price2_info.latest_close_price_date}現在)</p>
                </div>
                <div><img src="${json.stock_price2_info.stock_price_image}" alt="Image"></div>
            </div>
        </div>
        `

        // 画面をクリックしたら音声が流れるようにする
        const music = new Audio(json.voice_url);
        document.body.addEventListener('click', () => {
            music.play();
        });
    })
    .catch(error => {
        // エラーが発生したら再度読み込んでもらうよう表示
        hideLoadingError(error);
    });
}