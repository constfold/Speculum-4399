package speculum.interceptor
{
    import flash.net.URLLoader;
    import flash.net.URLRequest;
    import flash.events.Event;

    public class SpeculumInterceptorURLLoader extends URLLoader
    {
        private var request:URLRequest = null;

        public override function load(request:URLRequest):void
        {
            trace("Intercept: " + request.url);
            this.request = request;
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
            super.load(this.request);
        }
    }
}