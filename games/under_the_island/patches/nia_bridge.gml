/// nia_bridge.gml
/// Route B 注入腳本 — 在 GameMaker 對話觸發點呼叫妮婭 AI
///
/// 使用方式：
///   在妮婭對話觸發的 Object 事件中插入：
///   var _reply = nia_bridge_call(event_name, player_choice, room_get_name(room));
///   // 用 _reply 替換或補充遊戲原本的對話文字
///
/// 注意：GameMaker 不支援原生 HTTP，需搭配 HTTP extension 或 async event

/// @param {string} _event   事件名稱（例如 "gear_puzzle_solved"）
/// @param {string} _choice  玩家的選擇或行動描述
/// @param {string} _scene   目前場景/room 名稱
/// @return {string}         妮婭的 AI 回應文字
function nia_bridge_call(_event, _choice, _scene) {
    var _url = "http://localhost:7701/event";
    var _body = json_stringify({
        event: _event,
        player_choice: _choice,
        scene: _scene
    });
    var _headers = ds_map_create();
    ds_map_add(_headers, "Content-Type", "application/json");

    // 使用 GameMaker 內建 HTTP（async）
    var _req_id = http_request(_url, "POST", _headers, _body);
    ds_map_destroy(_headers);

    // 呼叫方需要在 Async - HTTP 事件中處理回應
    // 回傳 request id 供追蹤
    return _req_id;
}

/// 在 Async - HTTP 事件中加入：
///
/// if (async_load[? "id"] == global.nia_req_id) {
///     var _response = json_parse(async_load[? "result"]);
///     var _reply = _response.reply;
///     // 顯示 _reply 到對話框
///     global.nia_last_reply = _reply;
/// }
