function Notification(n,t){this.permission="granted",desktop.sendMessage(n,t.body)}Notification.permission="granted",Notification.requestPermission=function(n){void 0!=typeof n&&n()};var ScudCloud={init:function(){document.onpaste=function(){desktop.pasted(!1)},TS.ui.growls.getPermissionLevel=function(){return"granted"},TS.ui.growls.show=function(n,t,i,e,o,s,a){new Notification(n,{body:i,icon:TS.boot_data.img.app_icon,tag:"tag_"+(a?a.id||a.ts||(new Date).getTime():(new Date).getTime())})},ScudCloud.watch()},listChannels:function(){return TS.channels.getUnarchivedChannelsForUser()},watch:function(){setInterval(function(){var n=0;$("span.unread_highlight").not(".hidden").each(function(){n+=new Number($(this).text().replace("+",""))}),desktop.count(n.toString())},1e3)},join:function(n){return TS.channels.join(n)},setClipboard:function(n){TS.client.ui.file_pasted_sig.dispatch(n,TS.model.shift_key_pressed)}};ScudCloud.init(),ScudCloud.listChannels();
