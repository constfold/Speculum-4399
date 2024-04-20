package speculum.loader
{
	import flash.system.LoaderContext;
	import flash.system.ApplicationDomain;
	import flash.system.Security;
	import flash.display.Loader;
	import flash.events.Event;
	import flash.display.DisplayObject;
	import flash.events.DataEvent;
	import flash.utils.setTimeout;
	import flash.net.URLLoader;
	import flash.net.URLRequest;
	import unit4399.events.*;
	import flash.display.Loader;
	import flash.display.LoaderInfo;
	import flash.display.MovieClip;
	import flash.globalization.DateTimeFormatter;
	import flash.globalization.LocaleID;

	public class SpeculumLoader extends MovieClip
	{
		private var _loaderContext:LoaderContext;
		private var _loader:Loader;
		private var game:* = null;
		private var config:Object = null;
		private var formatter:DateTimeFormatter = new DateTimeFormatter(LocaleID.DEFAULT);

		public function SpeculumLoader(params:Object = null):void
		{
			super();
			Security.allowDomain("*");
			Security.allowInsecureDomain("*");
			this.formatter.setDateTimePattern("yyyy-MM-dd HH:mm:ss");
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

			var loader:Loader = new Loader();
			loader.contentLoaderInfo.addEventListener(Event.COMPLETE, this.onLoadComplete);
			loader.load(new URLRequest(this.config.gamefile), new LoaderContext(false, ApplicationDomain.currentDomain));
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

		private var logInfo:Object = null;
		public function get isLog():Object
		{
			trace("isLog");
			return this.logInfo;
		}

		public function showLogPanel():void
		{
			trace("showLogPanel");
			var log:Object = {
					uid: 1,
					name: "test"
				};
			this.logInfo = log;
			setTimeout(function():void
				{
					stage.dispatchEvent(new SaveEvent(SaveEvent.LOG, log));
				}, 500);
		}

		public function getServerTime():void
		{
			trace("getServerTime");
			setTimeout(function():void
				{
					stage.dispatchEvent(new DataEvent("serverTimeEvent", false, false, formatter.format(new Date())));
				}, 1000);
		}

		public function getData(ui:Boolean = true, index:Number = 0):void
		{
			trace("getData");
			var request:URLRequest = new URLRequest(config.server + "http://api.speculum.fake/save/get/" + index);
			var loader:URLLoader = new URLLoader();
			loader.addEventListener(Event.COMPLETE, function(e:Event):void
				{
					stage.dispatchEvent(new SaveEvent(SaveEvent.SAVE_GET, JSON.parse(e.target.data).data, true, false));
				});
			loader.load(request);
		}

		public function getList():void
		{
			trace("getList");
			var request:URLRequest = new URLRequest(config.server + "http://api.speculum.fake/save/list");
			var loader:URLLoader = new URLLoader();
			loader.addEventListener(Event.COMPLETE, function(e:Event):void
				{
					stage.dispatchEvent(new SaveEvent(SaveEvent.SAVE_LIST, JSON.parse(e.target.data), true, false));
				});
			loader.load(request);
		}

		public function saveData(title:String, data:Object, ui:Boolean = true, index:int = 0):void
		{
			trace("saveData");

			var request:URLRequest = new URLRequest(config.server + "http://api.speculum.fake/save/save");
			request.method = "POST";
			request.data = JSON.stringify( {
						"index": index,
						"title": title,
						"data": data,
						"datetime": formatter.format(new Date())
					});
			var loader:URLLoader = new URLLoader();
			loader.addEventListener(Event.COMPLETE, function(e:Event):void
				{
					stage.dispatchEvent(new SaveEvent(SaveEvent.SAVE_SET, true, true, false));
				});
			loader.load(request);
		}

		public function getBalance():void
		{
			trace("getBalance");
			setTimeout(function():void
				{
					stage.dispatchEvent(new PayEvent(PayEvent.GET_MONEY, {balance: 20000}, true, false));
				}, 500);
		}

		public function decMoney_As3(param1:int):void
		{
			trace("decMoney_As3");
			stage.dispatchEvent(new PayEvent(PayEvent.DEC_MONEY, {balance: 20000}, true, false));
		}

		public function getVariables(idx:int, ids:Array):void
		{
			trace("getVariables, idx: " + idx + ", ids: " + ids);
		}

		public function getStoreState():void
		{
			trace("getStoreState");
			setTimeout(function():void
				{
					stage.dispatchEvent(new DataEvent("StoreStateEvent", false, false, "1"));
				}, 500);
		}

		public function buyPropNd(param1:Object):void
		{
			trace("buyPropNd");
			param1.balance = 20000;
			setTimeout(function():void
				{
					stage.dispatchEvent(new ShopEvent(ShopEvent.SHOP_BUY_ND, param1, true, false));
				}, 500);
		}

		public function getTotalPaiedFun(exInfo:Object = null):void
		{
			trace("getTotalPaiedFun");
			setTimeout(function():void
				{
					stage.dispatchEvent(new PayEvent(PayEvent.PAY_MONEY, {balance: 20000}, true, false));
				}, 500);
		}

		public function getTotalRechargedFun(exInfo:Object = null):void
		{
			trace("getTotalRechargedFun");
			setTimeout(function():void
				{
					stage.dispatchEvent(new PayEvent(PayEvent.RECHARGED_MONEY, {balance: 20000}, true, false));
				}, 500);
		}

		public function submitScoreToRankLists(idx:uint, rankInfoAry:Array):void
		{
			trace("submitScoreToRankLists, idx: " + idx + ", rankInfoAry: " + rankInfoAry);
			setTimeout(function():void
				{
					stage.dispatchEvent(new RankListEvent(RankListEvent.RANKLIST_SUCCESS, {
									apiName: "3",
									data: [ {
											code: "1",
											message: "NOT SUPPORTED"
										}]
								}, true, false));
				}, 500);
		}
	}
}