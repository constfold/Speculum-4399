package speculum.interceptor
{
    import flash.net.URLLoader;
    import flash.net.URLRequest;
    import flash.events.Event;
    import flash.utils.ByteArray;

    public class SpeculumInterceptor extends URLLoader
    {
        private var request:URLRequest = null;
        public override function load(request:URLRequest):void
        {
            trace("Intercept: " + request.url);
            this.request = request;
            var prefixRequest:URLRequest = new URLRequest("prefix.txt");
            var prefixLoader:URLLoader = new URLLoader();
            prefixLoader.addEventListener(Event.COMPLETE, this.onResult);
            prefixLoader.load(prefixRequest);
        }

        public function onResult(event:Event):void
        {
            var prefix:String = event.target.data;
            trace("Prefix: " + prefix);
            // modify request
            this.request.url = prefix + this.request.url;
            super.load(this.request);
        }
    }
}