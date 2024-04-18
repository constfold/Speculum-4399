package speculum.loader
{
	import flash.system.LoaderContext;
	import flash.system.ApplicationDomain;
	import flash.system.Security;
	import flash.display.Loader;
	import flash.utils.ByteArray;
	import flash.events.Event;
	import flash.display.Sprite;
	import flash.display.DisplayObject;
	import flash.events.DataEvent;
	import flash.utils.setTimeout;
	import flash.net.SharedObject;
	import flash.net.URLLoader;
	import flash.net.URLRequest;
	import unit4399.events.*;
	import flash.display.Loader;
	import flash.display.LoaderInfo;
	import flash.display.MovieClip;

	public class SpeculumLoader extends MovieClip
	{
		private var _loaderContext:LoaderContext;
		private var _loader:Loader;
		private var game:* = null;
		private var config:Object = null;

		public function SpeculumLoader(params:Object = null):void
		{
			super();
			Security.allowDomain("*");
			Security.allowInsecureDomain("*");
			addEventListener(Event.ADDED_TO_STAGE, this.loadConfig);
		}

		private function loadConfig(e:Event):void
		{
			removeEventListener(Event.ADDED_TO_STAGE, this.loadConfig);
			var loader:URLLoader = new URLLoader();
			loader.addEventListener(Event.COMPLETE, this.loadGame);
			loader.load(new URLRequest("game.json"));
		}

		private function loadGame(e:Event):void
		{
			trace("loadGame");
			removeEventListener(Event.COMPLETE, this.loadGame);
			this.config = JSON.parse(e.target.data);

			var so:SharedObject = SharedObject.getLocal(this.config.saveName, this.config.savePath, false);
			if (!so.data.list)
			{
				so.data.list = [];
				for (var i:int = 0; i < 7; i++)
				{
					so.data.list[i] = null;
				}
			}

			var loader:Loader = new Loader();
			loader.contentLoaderInfo.addEventListener(Event.COMPLETE, this.onLoadComplete);
			loader.load(new URLRequest(this.config.gamefile));
		}

		private function onLoadComplete(e:Event):void
		{
			trace("onLoadComplete");
			removeEventListener(Event.COMPLETE, this.onLoadComplete);
			var loaderInfo:LoaderInfo = LoaderInfo(e.target);
			this.game = loaderInfo.content;
			try
			{
				this.game.setHold(this);
			}
			catch (e:Error)
			{
				trace(e);
			}
			this.addChild(this.game as DisplayObject);
			trace("ok");
		}

		/* API */

		public function get isLog():Object
		{
			trace("isLog");
			return {
					uid: 1,
					name: "test",
					type: ""
				};
		}

		public function showLogPanel():void
		{
			trace("showLogPanel");
		}

		public function getServerTime():void
		{
			trace("getServerTime");
			setTimeout(function():void
				{
					stage.dispatchEvent(new DataEvent("serverTimeEvent", true, false, "2000-01-01 00:00:00"));
				}, 500);
		}

		// public function getData(ui:Boolean = true, index:Number = 0):void
		// {
		// 	trace("getData");
		// 	var so:SharedObject = SharedObject.getLocal(this.config.saveName, this.config.savePath, false);
		// 	setTimeout(function():void
		// 		{
		// 			stage.dispatchEvent(new SaveEvent(SaveEvent.SAVE_GET, so.data.list[index], true, false));
		// 		}, 500);
		// }

		// public function getList():void
		// {
		// 	trace("getList");
		// 	var so:SharedObject = SharedObject.getLocal(this.config.saveName, this.config.savePath, false);
		// 	setTimeout(function():void
		// 		{
		// 			stage.dispatchEvent(new SaveEvent(SaveEvent.SAVE_LIST, so.data.list, true, false));
		// 		}, 500);
		// }

		// public function getBalance():void
		// {
		// 	trace("getBalance");
		// 	setTimeout(function():void
		// 		{
		// 			stage.dispatchEvent(new PayEvent(PayEvent.GET_MONEY, {balance: 20000}, true, false));
		// 		}, 500);
		// }

		// public function saveData(title:String, data:Object, ui:Boolean = true, index:int = 0):void
		// {
		// 	trace("saveData");
		// 	var so:SharedObject = SharedObject.getLocal(this.config.saveName, this.config.savePath, false);
		// 	so.data.list[index] = {
		// 			"index": index,
		// 			"title": title,
		// 			"data": data,
		// 			"datetime": "2000-01-01 00:00:00"
		// 		};
		// 	setTimeout(function():void
		// 		{
		// 			stage.dispatchEvent(new SaveEvent(SaveEvent.SAVE_SET, true, true, false));
		// 		}, 500);
		// }

		// public function decMoney_As3(param1:int):void
		// {
		// 	trace("decMoney_As3");
		// 	stage.dispatchEvent(new PayEvent(PayEvent.DEC_MONEY, {balance: 20000}, true, false));
		// }
	}
}