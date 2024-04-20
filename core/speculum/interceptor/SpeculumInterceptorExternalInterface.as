package speculum.interceptor
{
    import flash.net.URLLoader;
    import flash.net.URLRequest;

    public class SpeculumInterceptorExternalInterface
    {
        public function SpeculumInterceptorExternalInterface()
        {
        }

        public static function get available():Boolean
        {
            return false;
        }

        public static function get objectID():String
        {
            return "";
        }

        public static var marshallExceptions:Boolean;

        public static function addCallback(functionName:String, closure:Function):void
        {
            throw new Error("ExternalInterface is not available in this context.");
        }

        public static function call(functionName:String, ...rest:Array):*
        {
            trace("ExternalInterface call: " + functionName + "(" + rest.join(", ") + ")");
            if (functionName == "UniLogin.getUid")
            {
                return 1;
            }
            else if (functionName == "UniLogin.getUname")
            {
                return "test";
            }
            throw new Error("ExternalInterface is not available in this context.");
        }
    }
}