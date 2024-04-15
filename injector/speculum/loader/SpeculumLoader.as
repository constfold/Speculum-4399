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

	public class SpeculumLoader extends Sprite
	{
		private var _loaderContext:LoaderContext;
		private var _loader:Loader;
		private var gameHold:Sprite;
		private var game:* = null;

		public function SpeculumLoader(params:Object = null):void
		{
			this.gameHold = new Sprite();
			super();
			Security.allowDomain("*");
			Security.allowInsecureDomain("*");
			addEventListener(Event.ADDED_TO_STAGE, this.loadGame);
			var so:SharedObject = SharedObject.getLocal("gameData");
			if (!so.data.list)
			{
				so.data.list = [];
				for (var i:int = 0; i < 7; i++)
				{
					so.data.list[i] = null;
				}
			}
		}

		private function loadGame(e:Event):void
		{
			removeEventListener(Event.ADDED_TO_STAGE, this.loadGame);
			this.addChild(this.gameHold);

            var loader:URLLoader = new URLLoader();
            loader.addEventListener(Event.COMPLETE, this.onLoadComplete);
            loader.load(new URLRequest("_Game.swf"));
		}

        private function onLoadComplete(e:Event):void
        {
            var loader:URLLoader = URLLoader(e.target);
            var bytes:ByteArray = loader.data;
            this._loader = new Loader();
            this._loaderContext = new LoaderContext(false, ApplicationDomain.currentDomain);
            this._loader.loadBytes(bytes, this._loaderContext);
            this._loader.contentLoaderInfo.addEventListener(Event.COMPLETE, this.assetLoaded);
        }

		private function assetLoaded(e:Event):void
		{
			trace("Asset loaded");
			this._loader.contentLoaderInfo.removeEventListener(Event.COMPLETE, this.assetLoaded);
			this.game = e.target.content;

			try
			{
				this.game.setHold(this);
			}
			catch (e:Error)
			{
				trace(e);
			}
			this.gameHold.addChild(this.game as DisplayObject);
			trace("ok");
		}

        /* API */

		public function get isLog():Object
		{
			return {
					uid: 1,
					name: "test"
				};
		}

		public function showLogPanel():void
		{
		}

		public function getServerTime():void
		{
			trace("getServerTime");
			setTimeout(function():void
				{
					stage.dispatchEvent(new DataEvent("serverTimeEvent", true, false, "2000-01-01 00:00:00"));
				}, 500);
		}

		public function getData(ui:Boolean = true, index:Number = 0):void
		{
			trace("getData")
			var so:SharedObject = SharedObject.getLocal("gameData");
			setTimeout(function():void
				{
					stage.dispatchEvent(new SaveEvent(SaveEvent.SAVE_GET, so.data.list[index], true, false));
				}, 500);
		}

		public function getList():void
		{
			trace("getList")
			var so:SharedObject = SharedObject.getLocal("gameData");
			setTimeout(function():void
				{
					stage.dispatchEvent(new SaveEvent(SaveEvent.SAVE_LIST, so.data.list, true, false));
				}, 500);
		}

		public function getBalance():void
		{
			trace("getBalance")
			setTimeout(function():void
				{
					stage.dispatchEvent(new PayEvent(PayEvent.GET_MONEY, {balance: 20000}, true, false));
				}, 500);
		}

		public function saveData(title:String, data:Object, ui:Boolean = true, index:int = 0):void
		{
			trace("saveData")
			var so:SharedObject = SharedObject.getLocal("gameData");
			so.data.list[index] = {
					"index": index,
					"title": title,
					"data": data,
					"datetime": "2000-01-01 00:00:00"
				};
			setTimeout(function():void
				{
					stage.dispatchEvent(new SaveEvent(SaveEvent.SAVE_SET, true, true, false));
				}, 500);
		}

		public function decMoney_As3(param1:int):void
		{
			trace("decMoney_As3");
			stage.dispatchEvent(new PayEvent(PayEvent.DEC_MONEY, {balance: 20000}, true, false));
		}
	}
}