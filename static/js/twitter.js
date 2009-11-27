/*********************************************************************************
**
** The MIT License
**
** Copyright (c) 2009 Luis C. Cruz
** 
** Permission is hereby granted, free of charge, to any person obtaining a copy
** of this software and associated documentation files (the "Software"), to deal
** in the Software without restriction, including without limitation the rights
** to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
** copies of the Software, and to permit persons to whom the Software is
** furnished to do so, subject to the following conditions:
** 
** The above copyright notice and this permission notice shall be included in
** all copies or substantial portions of the Software.
** 
** THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
** IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
** FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
** AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
** LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
** OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
** THE SOFTWARE.
**
*********************************************************************************/

/**
* Constructor
**/
function Twitter(){
    
}

/**
* This class define a twitter user.
*
* At this momento only json format for response is implemented and uses
* JQuery to do ajax request and others.
* This class don't log in a the user, the session should be actived.
**/
prototype = {    
    // Urls for retrieve twitter data.
    url_profile: null,
    url_timeline: null,
    url_update: null,
    
    // this field will be called when the response is not valid params xhr, options and element
    callback_error: null,
    callback_success: null,
    
    element: null,
    
    // functions
    
    /**
    * @param element is the html element.
    * @error if url_profile is not defined 
    *
    * This function generates the elements inside the param element
    * using the data obtained by the request.
    * And this should be the first function called.
    **/
    get_profile: function(element){
        this.element = $(element);
        if (this.url_profile == null)
            throw new Error("URL for profile is not defined.");
        $.ajax({type: "GET",
                url: this.url_profile,
                dataType: "json",
                success: this._generate_element,
                error: this._on_error});
    },
    
    /**
    * This function should be the callback for get_profile function.
    **/
    _generate_element: function(data, textStatus){
        var instance = get_twitter_object();
        
        // creating the base html structure
        var div = $("<div><div id='profile-twitter'></div><div id='twitts'></div></div>");
        div.css("background-image", data["profile_background_image_url"]);
        div.css("background-color", data["profile_background_color"]);
        
        var profile = "<img src='" + data["profile_image_url"] + "' width='50' height='50'/>";
        profile += "<div style='display:inline-block; padding:15px;'><p> <span class='twitt-user'></span>&nbsp;&nbsp;|&nbsp;&nbsp;<a class='disconnect' href='/twitter/logout/'>Disconnect</a></p>Created at: " + data["created_at"] + "<br/>Twitts: " + data["statuses_count"] + "</div>";
        profile = $(profile);
        profile.find(".twitt-user").text(data["screen_name"]);
        
        div.find("#profile-twitter").css("color", data["profile_text_color"])
                                    .append(profile);
        
        instance.element.html(div);
        
        if (instance.callback_success)
            instance.callback_success(this, instance.element);
    },
    
    /**
    * This function should be callback for every request did by an object
    * instance of this class.
    * Clear the element field and call the callback function with the params.
    **/
    _on_error: function(xhr, textStatus, thrownError){
        var instance = get_twitter_object();
        if (xhr && xhr.readyState > 1){
            var element = $(instance.element);
            element.html("");
            if (instance.callback_error)
                instance.callback_error(xhr, element);
        }
    },
    
    load_timeline: function(){
        if (this.url_timeline == null)
            throw new Error("URL for timeline is not defined.");
        $.ajax({type: "GET",
                url: this.url_timeline,
                dataType: "json",
                success: this._generate_timeline,
                error: this._on_error});
    },
    
    _generate_timeline: function(data, textStatus){
        var instance = get_twitter_object();
        var element = instance.element.find("#twitts").html("");
        for (index in data)
            element.append(instance._generate_twitt(data[index]));
        if (instance.callback_success)
            instance.callback_success(this, instance.element);
    },
    
    _generate_twitt: function(twitt){
        var html = "<div style='border: 1px solid white; padding: 10px;'><div><img src='" + twitt["user"]["profile_image_url"] + "' width='50' height='50'/>";
        html += "<p class='twitt-twitter'></p></div>"; // screen name
        html += "<div> <p class='twitt-text'></p>" // twitt
        html += "<p> At " + twitt["created_at"] + " from " + twitt["source"] +"</p></div></div>";
        html = $(html);
        
        html.find(".twitt-twitter").text(twitt["user"]["screen_name"]);
        html.find(".twitt-text").text(twitt["text"]);
        return html;
    },
    
    send_twitt: function(text){
        if (this.url_update == null)
            throw new Error("URL for update is not defined.");
        if (text != ""){
            $.ajax({type: "POST",
                url: this.url_update,
                data: {status: text},
                dataType: "json",
                success: this._twitt_sent,
                error: this._on_error});
        }
    },
    
    _twitt_sent: function(data, textStatus){
        var instance = get_twitter_object();
        var element = instance.element.find("#twitts");
        element.prepend(instance._generate_twitt(data));
        if (instance.callback_success)
            instance.callback_success(this, instance.element);
    },
};

$.extend(Twitter.prototype, prototype);

function get_twitter_object(){
    return twitter_user;
}

// Global variable for a Twitter object instance
var twitter_user = new Twitter();