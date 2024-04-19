package speculum.interceptor
{
    import flash.display.Loader;
    import flash.net.URLRequest;
    import flash.system.LoaderContext;
    import flash.net.URLLoader;
    import flash.events.Event;
    import flash.net.URLLoaderDataFormat;

    public class SpeculumInterceptorLoader extends Loader
    {
        private var request:URLRequest = null;
        private var context:LoaderContext = null;

        override public function load(request:URLRequest, context:LoaderContext = null):void
        {
            trace("Intercept: " + request.url);
            this.request = request;
            this.context = context;
            var configLoader:URLLoader = new URLLoader();
            configLoader.addEventListener(Event.COMPLETE, this.onResult);
            configLoader.load(new URLRequest("game.json"));
        }

        private function onResult(event:Event):void
        {
            removeEventListener(Event.COMPLETE, this.onResult);
            var config:Object = JSON.parse(event.target.data);
            // modify request
            this.request.url = config.server + this.request.url;
            trace("Intercepted: " + this.request.url);
            // workaround for security policy
            var loader:URLLoader = new URLLoader();
            loader.addEventListener(Event.COMPLETE, this.onLoaded);
            loader.dataFormat = URLLoaderDataFormat.BINARY;
            loader.load(this.request);
        }

        private function onLoaded(event:Event):void
        {
            loadBytes(event.target.data, this.context);
        }
    }
}